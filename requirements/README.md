# Files

The usual `requirements.txt` file is split up in multiple files for different environments. Multiple files can be combined: `pip install -r requirements/development.txt -r requirements/testing.txt`

- `development.txt`: no limits on the versions, always use the latest version for all dependencies. This allows us to quickly discover and respond to changes in the packages we depend on. The idea is to have occasional small changes that require fixing, rather than one large pile of fixes that need to be addressed all at once.
- `production.txt`: exact version limits on all dependencies, to "freeze" the dependencies in a known working state.
- `testing.txt`: additional packages for testing.
- `documentation.txt`: additional packages for building documentation.

# Dependencies

Keep a list of dependencies here with date and reason why we need it. This will help in future to get rid of unneeded dependencies. Use the pip install name in this list, not the import name. This may differ in case (i.e. `pip install Flask` vs. `import flask`) or underscore (`pip install requests-oauthlib` vs `import requests_oauthlib`).

|--------------------|----------------|-----------------------------|
|Package name        |Date added      |Reason                       |
|--------------------|----------------|-----------------------------|


