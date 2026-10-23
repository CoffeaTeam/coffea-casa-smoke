# Collection of coffea-casa-smoke tests

Lightweight smoke tests to verify basic coffea-casa functionality and CI/deployment health.

For now we support next services:

- Dask scaling at facility
- ROOT and Dask at scale at facility
- CMS Combine
- ServiceX

## What this repository does
Provides a small suite of fast, focused smoke tests that exercise core coffea-casa functionality (importing the package, simple analysis execution, and basic job submission/workflow checks). The tests are intended to run quickly in local and CI environments to detect regressions early.

This repository is designed to integrate easily with Kubernetes Jobs.

## AGC analyses

`agc/` holds analyses from [iris-hep/analysis-grand-challenge](https://github.com/iris-hep/analysis-grand-challenge),
pinned to the upstream commit in `agc/_sync/upstream.toml`. Local changes are recorded in `agc/_sync/patches/`.

```bash
agc/_sync/sync.py sync --ref main   # update to upstream main, 3-way merging local changes
agc/_sync/sync.py refresh-patches   # after editing files under agc/, record the change
agc/_sync/sync.py check             # verify agc/ == upstream + patches (runs in CI)
```

A weekly GitHub Action opens an `agc-sync` PR. If the local patches don't merge cleanly, the PR is a draft
with conflict markers to resolve. Which upstream files are synced is set by `include` in `upstream.toml`.

## License
See the LICENSE file in the repository for license details.
