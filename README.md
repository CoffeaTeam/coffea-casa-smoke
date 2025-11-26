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

## License
See the LICENSE file in the repository for license details.
