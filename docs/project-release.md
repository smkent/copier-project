---
title: Releasing a project
icon: lucide/rocket
---

# Releasing a project

Release version numbers should follow [Semantic Versioning][semver].

To create a release, run `mise run release -n` with one of `patch`, `minor`, or
`major` corresponding to the version number component to update.

```sh
mise run release -n patch|minor|major
```

This will display the new version number that would be created and pushed
automatically using [bump-my-version][bump-my-version] (for example, `v1.2.3`).

!!! info

    Always run `mise run release` with `-n` or `--dry-run` first to preview the
    tag that would be pushed!

After confirming everything looks right, run the same command again without `-n`
to create and push the release tag:

```sh
mise run release patch|minor|major
```

* A corresponding GitHub release will be created automatically.
* If PyPI publishing is enabled, a release package will be built and uploaded to
  PyPI.
* If container image build and publishing is enabled, a container image will be
  built and published to the [GitHub Container Registry (GHCR)][ghcr-docs].

[bump-my-version]: https://callowayproject.github.io/bump-my-version/
[ghcr-docs]: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
[semver]: https://semver.org/
