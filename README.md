# copier-project

[Copier][copier] template for software projects with modern tooling

[![Copier][copier-badge]][copier]
[![License](https://img.shields.io/github/license/smkent/copier-project)](https://github.com/smkent/copier-project/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/copier-project)](https://pypi.org/project/copier-project/)
[![Python](https://img.shields.io/pypi/pyversions/copier-project)](https://pypi.org/project/copier-project/)
[![GitHub stars](https://img.shields.io/github/stars/smkent/copier-project?style=social)](https://github.com/smkent/copier-project)

## Quick start

Install required software:

- [**mise-en-place**][mise]: `curl https://mise.run | sh` or
  [alternate installation method][mise-installation]
- [**Copier**][copier]: `mise use -g copier` or `uv tool install copier`

Create a new project from the template:

```sh
copier copy "gh:smkent/copier-project" /new/project/path
```

**[For more details, see the documentation!][docs-usage]**

## Variants and features

The **Generic** project variant is a language-agnostic project template with
features common to all project variants:

* [**mise-en-place**][mise] ("mise") for development toolchain management

    [![mise][mise-badge]][mise]

* [**prek**][prek] for [pre-commit][pre-commit] compatible git hooks, with
  [**GitHub Actions**][github-actions] CI workflow

    [![prek][prek-badge]][prek]

* Contribution terms including selectable LLM use policy, with commit message
  checks by [**commit-check**][commit-check]

    [![commit-check][commit-check-badge]][commit-check]

* Update automation with [**Renovate**][renovate] and
  [**`copier update`**][copier-update]

    [![Copier][copier-badge]][copier-update]
    [![renovate][renovate-badge]][renovate]

* [**Zensical**][zensical] project documentation with automatic deployment to
  [**GitHub Pages**][github-pages]

### Python

The **Python** project variant adds Python-specific features:

* [Astral][astral] toolset: [**uv**][uv], [**ruff**][ruff], and [**ty**][ty]

    [![uv][uv-badge]][uv]
    [![ruff][ruff-badge]][ruff]
    [![ty][ty-badge]][ty]

* [**PyPI package**][pypi] and [**container image**][ghcr-docs] release
  automation via [**GitHub Actions**][github-actions]
* [**pytest**][pytest] test framework with [**codecov.io**][codecovio] support

## Credits

This template was inspired by [pawamoy/copier-uv][copier-uv] and
[ritwiktiwari/copier-astral][copier-astral] -- Thanks!

## License

Copyright (C) 2026 Stephen Kent and contributors

Licensed under the MIT License
([`MIT`](https://github.com/smkent/copier-project/blob/main/LICENSE)).

[astral]: https://astral.sh
[codecovio]: https://codecov.io
[commit-check]: https://commit-check.com
[commit-check-badge]: https://commit-check.com/badge.svg
[copier-astral]: https://ritwiktiwari.github.io/copier-astral/
[copier-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json
[copier-update]: https://copier.readthedocs.io/en/stable/updating/
[copier-uv]: https://pawamoy.github.io/copier-uv/
[copier]: https://copier.readthedocs.io
[docs-usage]: https://smkent.github.io/copier-project/requirements/
[ghcr-docs]: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
[github-actions]: https://github.com/features/actions
[github-pages]: https://pages.github.com
[mise]: https://mise.jdx.dev
[mise-installation]: https://mise.jdx.dev/installing-mise.html
[mise-badge]: https://mise-versions.jdx.dev/badge.svg
[pre-commit]: https://pre-commit.com/
[prek-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json
[prek]: https://prek.j178.dev/
[pypi]: https://pypi.org
[pytest]: https://docs.pytest.org
[renovate-badge]: https://img.shields.io/badge/renovate-enabled-brightgreen.svg?logo=renovatebot
[renovate]: https://docs.renovatebot.com/
[ruff-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[ruff]: https://docs.astral.sh/ruff/
[ty-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json
[ty]: https://docs.astral.sh/ty/
[uv-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json
[uv]: https://docs.astral.sh/uv/
[zensical]: https://zensical.org/
