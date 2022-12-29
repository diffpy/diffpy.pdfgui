$PROJECT = 'diffpy.pdfgui'
$ACTIVITIES = [
              'tag',  # Creates a tag for the new version number
              'push_tag',  # Pushes the tag up to the $TAG_REMOTE
              'pypi',  # Sends the package to pypi
              'ghrelease'  # Creates a Github release entry for the new tag
               ]
$PUSH_TAG_REMOTE = 'git@github.com:diffpy/diffpy.pdfgui.git'  # Repo to push tags to
$GITHUB_ORG = 'diffpy'  # Github org for Github releases and conda-forge
$GITHUB_REPO = 'diffpy.pdfgui'  # Github repo for Github releases  and conda-forge
$GHRELEASE_PREPEND = """See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

The release is also available at [PyPI](https://pypi.org/project/diffpy.pdfgui/) and [Conda](https://anaconda.org/conda-forge/diffpy.pdfgui).
"""  # release message
