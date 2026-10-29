---
title: Project variants
icon: lucide/flask-conical
---

# Project variants

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

### Python

The **Python** project variant adds Python-specific features:

* [Astral][astral] toolset: [**uv**][uv], [**ruff**][ruff], and [**ty**][ty]

    [![uv][uv-badge]][uv]
    [![ruff][ruff-badge]][ruff]
    [![ty][ty-badge]][ty]

* [**PyPI package**][pypi] and [**container image**][ghcr-docs] release
  automation via [**GitHub Actions**][github-actions]
* [**pytest**][pytest] test framework with [**codecov.io**][codecovio] support
* [**Zensical**][zensical] project documentation with automatic deployment to
  [**GitHub Pages**][github-pages]

[astral]: https://astral.sh
[codecovio]: https://codecov.io
[commit-check]: https://commit-check.com
[commit-check-badge]: https://commit-check.com/badge.svg
[copier-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json
[copier-update]: https://copier.readthedocs.io/en/stable/updating/
[ghcr-docs]: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
[github-actions]: https://github.com/features/actions
[github-pages]: https://pages.github.com
[mise]: https://mise.jdx.dev
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
