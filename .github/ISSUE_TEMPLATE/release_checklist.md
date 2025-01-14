---
name: Release
about: Checklist and communication channel for PyPI and GitHub release
title: "Ready for <version-number> PyPI/GitHub release"
labels: "release"
assignees: ""
---

### PyPI/GitHub rc-release preparation checklist:

- [ ] All PRs/issues attached to the release are merged.
- [ ] All the badges on the README are passing.
- [ ] License information is verified as correct. If you are unsure, please comment below.
- [ ] Locally rendered documentation contains all appropriate pages, including API references (check no modules are
      missing), tutorials, and other human-written text is up-to-date with any changes in the code.
- [ ] Installation instructions in the README, documentation, and the website (e.g., diffpy.org) are updated.
- [ ] Successfully run any tutorial examples or do functional testing with the latest Python version.
- [ ] Grammar and writing quality are checked (no typos).
- [ ] Install `pip install build twine`, run `python -m build` and `twine check dist/*` to ensure that the package can be built and is correctly formatted for PyPI release.

Please mention @sbillinge here when you are ready for PyPI/GitHub release. Include any additional comments necessary, such as version information and details about the pre-release here:

### PyPI/GitHub full-release preparation checklist:

- [ ] Create a new conda environment and install the rc from PyPI (`pip install <package-name>==??`)
- [ ] License information on PyPI is correct.
- [ ] Docs are deployed successfully to `https://www.diffpy.org/<package-name>`.
- [ ] Successfully run all tests, tutorial examples or do functional testing.

Please let @sbillinge know that all checks are done and the package is ready for full release.

### conda-forge release preparation checklist:

<!-- After @sbillinge releases the PyPI package, please check the following when creating a PR for conda-forge release.-->

- [ ] Ensure that the full release has appeared on PyPI successfully.
- [ ] New package dependencies listed in `conda.txt` and `test.txt` are added to `meta.yaml` in the feedstock.
- [ ] Close any open issues on the feedstock. Reach out to @bobleesj if you have questions.
- [ ] Tag @sbillinge and @bobleesj for conda-forge release.

### Post-release checklist

<!-- Before closing this issue, please complete the following: -->

- [ ] Run tutorial examples and conduct functional testing using the installation guide in the README. Attach screenshots/results as comments.
- [ ] Documentation (README, tutorials, API references, and websites) is deployed without broken links or missing figures.
