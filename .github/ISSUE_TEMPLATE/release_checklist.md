---
name: Release
about: Checklist and communication channel for PyPI and GitHub release
title: "Ready for <version-number> PyPI/GitHub release"
labels: "release"
assignees: ""
---

### PyPI/GitHub release checklist:

- [ ] All PRs/issues attached to the release are merged.
- [ ] All the badges on the README are passing.
- [ ] License information is verified as correct. If you are unsure, please comment below.
- [ ] Locally rendered documentation contains all appropriate pages, including API references (check no modules are
  missing), tutorials, and other human written text is up-to-date with any changes in the code.
- [ ] Installation instructions in the README, documentation and on the website (e.g., diffpy.org) are updated.
- [ ] Successfully run any tutorial examples or do functional testing with the latest Python version.
- [ ] Grammar and writing quality are checked (no typos).

Please mention @sbillinge here when you are ready for PyPI/GitHub release. Include any additional comments necessary, such as
version information and details about the pre-release here:

### conda-forge release checklist:

<!-- After @sbillinge releases the PyPI package, please check the following when creating a PR for conda-forge release.-->

- [ ] New package dependencies listed in `conda.txt` and `test.txt` are added to `meta.yaml` in the feedstock.
- [ ] All relevant issues in the feedstock are addressed in the release PR.

### Post-release checklist

<!-- Before closing this issue, please complete the following: -->

- [ ]  Run tutorial examples and conduct functional testing using the installation guide in the README. Attach screenshots/results as comments.
- [ ]  Documentation (README, tutorials, API references, and websites) is deployed without broken links or missing figures.
