# Changelog

## 1.0.0

Code base refactored for future maintenance and updated the dependencies for
security.

### Breaking changes

`SERVER_NAME` is no longer supported as the dependency flask-pyoidc deprecated
its use. Now, OIDC_REDIRECT_URI should be used instead to contain the full
redirect uri registered with the identity provider.

### Commits since 0.2.1

- Use a markdown CHANGELOG.md
- Install frozen environment where it matters
- Stop using PBR, stick with the basics
- Transition SERVER_NAME config to OIDC_REDIRECT_URI config
- Refreeze dependencies after bumping flask-pyoidc from 3.2 to 3.7
- pip-compile with py38
- Remove travis remnants
- Add .flake8 from JupyterHub
- Sort lines ascending
- Remove requirements.txt pre-commit fixer
- Add pre-commit hooks
- Run prettier on 403.html
- Run prettier on README.md
- Add newline at end of file
- Remove pyflakes in favor of flake8
- Remove pipfile remnants
- Migrate from pipenv to pip and pip-compile
- Partially please flake8
- Apply black autoformatting
- ci: migrate from travis to github workflows
- Update ChangeLog

## 0.2.1

- Bump flask-pyoidc to 3.2
- Trim Docker image size
- Ensures tests run against an updated Pipfile.lock
- Fix docker hub build badge
- Fix issues reported by pytest --flakes
- Fix initial .travis.yml setup
- Add CD to PyPI with TravisCI
- Update release instructions regarding Docker images
- Add PyPI / DockerHub badges
- Update release instructions in README.md
- Update ChangeLog

## 0.2.0

- Bump flask to 1.1 and flask-pyoidc to 3.1
- Update release instructions in README

## 0.1.9

- Fix a bug in the error handler
- Add small note to README
- Add ChangeLog

## 0.1.8

- Add notes on timeout settings
- Update package versions to get security fix
- Refactor indentation
- Update changelog

## 0.1.7

- Refresh README
- Align with default value change to https

## 0.1.6

- Add notes about PREFERRED_URL_SCHEME
- Add notes on DEBUG
- Add OIDC_EXTRA_AUTH_REQUEST_PARAMS
- Fix typo
- Increase uWSGI buffer size, for long query params

## 0.1.5

- Fix discourse\_ prefix bug
- Things works!

## 0.1.4

- Ensure strings when building up the query params
- Note about deployment

## 0.1.3

- Added logging etc..
- Add inline note about /health
- Readme instructions / test detail

## 0.1.2

- Add /health endpoint and test
- Add .vscode to gitignore
- Readme fixes

## 0.1.1

- Reworked Dockerization
- Update docstrings
- Redundant LICENCE stuff removed
- Lots of tests added
- Finetune tests
- Fixed configuration issues
- Things i need to revert soon..
- SERVER_NAME was very important ^^
- A lot of work to Dockerize it functionally..
- Started using create_app() for Dockerization
- Add note about this not being ready for use
- Ready for test deployment
- Cleanup old test
- Too many changes in one commit..
- Fix dependencies etc
- Define known discourse sso attributes
- Standing on the shoulders of giants
- Refactor structure
- README.md details
- Update package info
- Update README with PyPI dev instructions
- Initialize .gitignore
- Initialize pipenv
- Update README.md preliminary
- Prelim setup.py adjustments
- Boilerplate setup.py
- Initial python package foundation
