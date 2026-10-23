#!/usr/bin/env python3
"""Sync AGC analyses from iris-hep/analysis-grand-challenge.

The pinned upstream commit and the file selection live in upstream.toml.
Local modifications are recorded as patches/<analysis>.patch, a diff of
dest against the pristine upstream files at the pinned ref.

    sync.py sync [--ref REF]   move to REF (default: pinned ref), 3-way merging
                               local modifications; leaves conflict markers and
                               exits 2 on conflicts
    sync.py refresh-patches    rewrite patches/ from the current tree
    sync.py check              fail if the tree differs from upstream + patches
"""

import argparse
import fnmatch
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONFIG = HERE / "upstream.toml"
PATCHES = HERE / "patches"
IGNORED_PARTS = {"__pycache__", ".ipynb_checkpoints"}


def git(*args, cwd=None, input=None, check=True):
    return subprocess.run(
        ["git", *args], cwd=cwd, input=input, capture_output=True, check=check
    )


class Upstream:
    """Shallow fetches of the upstream repo into a scratch directory."""

    def __init__(self, repo, workdir):
        self.repo = repo
        self.dir = Path(workdir) / "upstream"
        git("init", "-q", str(self.dir))

    def resolve(self, ref):
        git("fetch", "-q", "--depth", "1", self.repo, ref, cwd=self.dir)
        return git("rev-parse", "FETCH_HEAD", cwd=self.dir).stdout.decode().strip()

    def files(self, sha, src, include):
        """Return {path relative to src: bytes} for files matching include."""
        out = git("ls-tree", "-r", "-z", "--name-only", sha, "--", src, cwd=self.dir)
        result = {}
        for path in filter(None, out.stdout.decode().split("\0")):
            rel = path[len(src) + 1 :]
            if any(matches(rel, pattern) for pattern in include):
                result[rel] = git("show", f"{sha}:{path}", cwd=self.dir).stdout
        return result


def matches(rel, pattern):
    if pattern.endswith("/**"):
        return rel.startswith(pattern[:-2])
    return fnmatch.fnmatchcase(rel, pattern)


def local_files(analysis):
    """Return {path relative to dest: bytes} for synced files currently in dest."""
    dest = ROOT / analysis["dest"]
    keep = set(analysis.get("local", []))
    result = {}
    for path in sorted(dest.rglob("*")) if dest.exists() else []:
        rel = path.relative_to(dest).as_posix()
        if path.is_file() and rel not in keep and not IGNORED_PARTS & set(path.parts):
            result[rel] = path.read_bytes()
    return result


def write_tree(root, files):
    for rel, data in files.items():
        path = Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def make_patch(dest, pristine, current):
    """Diff pristine -> current, with paths relative to the repo root."""
    with tempfile.TemporaryDirectory() as tmp:
        git("init", "-q", tmp)
        write_tree(Path(tmp) / dest, pristine)
        git("add", "-A", cwd=tmp)
        git("-c", "user.name=sync", "-c", "user.email=sync@localhost",
            "commit", "-q", "--allow-empty", "-m", "pristine", cwd=tmp)
        shutil.rmtree(Path(tmp) / dest, ignore_errors=True)
        write_tree(Path(tmp) / dest, current)
        git("add", "-A", cwd=tmp)
        return git("diff", "--cached", "--binary", "--no-color", cwd=tmp).stdout


def apply_patch(dest, pristine, patch):
    """Return pristine with patch applied, as {path relative to dest: bytes}."""
    with tempfile.TemporaryDirectory() as tmp:
        git("init", "-q", tmp)
        write_tree(Path(tmp) / dest, pristine)
        if patch:
            proc = git("apply", "--binary", "-", cwd=tmp, input=patch, check=False)
            if proc.returncode:
                sys.exit(f"{dest}: stored patch does not apply:\n{proc.stderr.decode()}")
        root = Path(tmp) / dest
        if not root.exists():
            return {}
        return {
            p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*")
            if p.is_file()
        }


def deleted_paths(dest, patch):
    """Paths (relative to dest) the stored patch deletes."""
    deleted, current = set(), None
    for line in patch.decode(errors="replace").splitlines():
        if m := re.match(r"diff --git a/(\S+) b/", line):
            current = m.group(1)
        elif line.startswith("deleted file mode") and current:
            deleted.add(current[len(dest) + 1 :])
    return deleted


def is_binary(data):
    return b"\0" in data[:8000]


def merge(rel, path, base, theirs, ours, ref):
    """3-way merge of one file into path. Return True if it conflicted."""
    if ours == theirs:
        return False
    if ours == base:
        path.write_bytes(theirs)
        print(f"  updated  {rel}")
        return False
    if base == theirs:
        return False
    if is_binary(ours) or is_binary(theirs):
        print(f"  CONFLICT (binary, kept local) {rel}")
        return True
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "base").write_bytes(base)
        (Path(tmp) / "theirs").write_bytes(theirs)
        proc = git(
            "merge-file", "-L", "local", "-L", "upstream (old)", "-L", f"upstream {ref[:10]}",
            str(path), str(Path(tmp) / "base"), str(Path(tmp) / "theirs"), check=False,
        )
    if proc.returncode:
        print(f"  CONFLICT {rel}")
        return True
    print(f"  merged   {rel}")
    return False


def sync_analysis(name, analysis, upstream, old_sha, new_sha):
    dest, src, include = analysis["dest"], analysis["src"], analysis["include"]
    patch_file = PATCHES / f"{name}.patch"
    patch = patch_file.read_bytes() if patch_file.exists() else b""
    old = upstream.files(old_sha, src, include)
    new = upstream.files(new_sha, src, include)
    current = local_files(analysis)
    deleted = deleted_paths(dest, patch)
    conflicts = False

    print(f"{name}:")
    for rel in sorted(old.keys() | new.keys()):
        path = ROOT / dest / rel
        base, theirs, ours = old.get(rel), new.get(rel), current.get(rel)
        if theirs is None:
            # removed upstream
            if ours is None or ours == base:
                path.unlink(missing_ok=True)
                print(f"  removed  {rel}")
            else:
                print(f"  CONFLICT (removed upstream, modified locally) {rel}")
                conflicts = True
        elif ours is None:
            if rel in deleted and base is not None:
                if base != theirs:
                    print(f"  note: {rel} is deleted locally but changed upstream")
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(theirs)
            print(f"  added    {rel}")
        elif base is None:
            # new upstream, but a local file already sits there
            if ours != theirs:
                print(f"  CONFLICT (added upstream, exists locally) {rel}")
                conflicts = True
        else:
            conflicts |= merge(rel, path, base, theirs, ours, new_sha)
    return conflicts


def refresh_patch(name, analysis, upstream, sha):
    pristine = upstream.files(sha, analysis["src"], analysis["include"])
    patch = make_patch(analysis["dest"], pristine, local_files(analysis))
    patch_file = PATCHES / f"{name}.patch"
    if patch:
        PATCHES.mkdir(exist_ok=True)
        patch_file.write_bytes(patch)
        print(f"wrote {patch_file.relative_to(ROOT)}")
    elif patch_file.exists():
        patch_file.unlink()
        print(f"removed {patch_file.relative_to(ROOT)} (no local changes)")


def check_analysis(name, analysis, upstream, sha):
    patch_file = PATCHES / f"{name}.patch"
    patch = patch_file.read_bytes() if patch_file.exists() else b""
    pristine = upstream.files(sha, analysis["src"], analysis["include"])
    expected = apply_patch(analysis["dest"], pristine, patch)
    actual = local_files(analysis)
    bad = sorted(
        rel for rel in expected.keys() | actual.keys()
        if expected.get(rel) != actual.get(rel)
    )
    for rel in bad:
        print(f"{name}: {analysis['dest']}/{rel} differs from upstream + patch")
    return not bad


def set_ref(sha):
    text = CONFIG.read_text()
    CONFIG.write_text(re.sub(r'(?m)^ref = ".*"$', f'ref = "{sha}"', text, count=1))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sync_p = sub.add_parser("sync", help="update to an upstream ref")
    sync_p.add_argument("--ref", help="upstream branch, tag or commit (default: pinned ref)")
    sub.add_parser("refresh-patches", help="regenerate patches from the current tree")
    sub.add_parser("check", help="verify the tree matches upstream + patches")
    args = parser.parse_args()

    config = tomllib.loads(CONFIG.read_text())
    analyses = config["analyses"]
    with tempfile.TemporaryDirectory() as tmp:
        upstream = Upstream(config["repo"], tmp)
        old_sha = upstream.resolve(config["ref"])

        if args.command == "check":
            ok = all([check_analysis(n, a, upstream, old_sha) for n, a in analyses.items()])
            if not ok:
                sys.exit("Run `agc/_sync/sync.py refresh-patches` to record local changes.")
            print(f"OK: agc matches upstream {old_sha[:10]} + patches")
            return

        if args.command == "refresh-patches":
            for name, analysis in analyses.items():
                refresh_patch(name, analysis, upstream, old_sha)
            return

        new_sha = upstream.resolve(args.ref or config["ref"])
        print(f"upstream {old_sha[:10]} -> {new_sha[:10]}")
        conflicts = False
        for name, analysis in analyses.items():
            conflicts |= sync_analysis(name, analysis, upstream, old_sha, new_sha)
        set_ref(new_sha)
        if conflicts:
            print(
                "\nConflicts left in the tree. Resolve them, then run "
                "`agc/_sync/sync.py refresh-patches`.",
                file=sys.stderr,
            )
            sys.exit(2)
        for name, analysis in analyses.items():
            refresh_patch(name, analysis, upstream, new_sha)


if __name__ == "__main__":
    main()
