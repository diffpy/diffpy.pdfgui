$PROJECT = 'diffpy.pdfgui'
$ACTIVITIES = [
              'version_bump',
              'changelog',
              'tag',  # Creates a tag for the new version number
              'push_tag',  # Pushes the tag up to the $TAG_REMOTE
              'pypi',  # Sends the package to pypi
              'ghrelease'  # Creates a Github release entry for the new tag
               ]
$VERSION_BUMP_PATTERNS = [
    ('regolith/__init__.py', '__version__\s*=.*', "__version__ = '$VERSION'"),
    ('setup.py', 'version\s*=.*,', "version='$VERSION',")
    ]
$CHANGELOG_FILENAME = 'CHANGELOG.rst'
$CHANGELOG_IGNORE = ['TEMPLATE.rst']
$PUSH_TAG_REMOTE = 'git@github.com:diffpy/diffpy.pdfgui.git'  # Repo to push tags to

$GITHUB_ORG = 'diffpy'  # Github org for Github releases and conda-forge
$GITHUB_REPO = 'diffpy.pdfgui'  # Github repo for Github releases  and conda-forge
$GHRELEASE_PREPEND = """See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

The release is also available at [PyPI](https://pypi.org/project/diffpy.pdfgui/) and [Conda](https://anaconda.org/conda-forge/diffpy.pdfgui).
"""  # release message
