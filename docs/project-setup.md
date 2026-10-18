---
title: Completing setup
icon: lucide/settings
---

# Completing project setup

!!! tip
    If you selected **Enable documentation site** during project creation,
    these instructions are also present in your new project along with links
    directly to your project's specific settings pages! To view:

    1. Start the local documentation server: `mise run docs`
    2. In your browser:

        1. Open **<http://localhost:8000>**
        2. Navigate to **Project Operations** → **One time setup**


## GitHub repository

[Repository Settings → General][github-settings-docs]:

- [x] Allow merge commits
- [x] Allow squash merging
- [ ] Allow rebase merging
- [x] Automatically delete head branches

Repository Settings → Branches → Add branch protection rule for the default branch
(`main`):

- [x] Restrict deletions
- [x] Require a pull request before merging
- [x] Block force pushes

## Renovate

Ensure the [Renovate app][renovate] is installed on your account, then enable
it for your repository.

## PyPI publishing

!!! info "Only needed if your project will publish packages to PyPI"

This template uses [trusted publishing][pypi-trusted-publishing] so no API
tokens need to be stored as secrets.

1. On PyPI, add a (pending) trusted publisher in your
   [Trusted Publisher Management][pypi-publishing-settings] settings:
     - Publisher: GitHub Actions
     - Owner: `<your-github-user>`
     - Repository: `<your-project-name>`
     - Workflow: `release.yaml`
     - Environment: `pypi`
2. Create the `pypi` environment in the GitHub repository:
   Repository Settings → Environments → New environment → `pypi`
3. Publish a release by pushing a tag:
   ```sh
   git tag v0.1.0  # or your desired first version number
   git push --tags
   ```

## Container registry (ghcr.io)

!!! info "Only needed if your project will build and publish container images"

Enable write access for Actions:

Repository Settings → Actions → General → Workflow permissions
→ Read and write permissions

## GitHub Pages

!!! info "Only needed if your project will publish the documentation site"

Repository Settings → Pages → Source → GitHub Actions

[github-settings-docs]: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features
[pypi-publishing-settings]: https://pypi.org/manage/account/publishing/
[pypi-trusted-publishing]: https://docs.pypi.org/trusted-publishers/
[renovate]: https://github.com/apps/renovate
