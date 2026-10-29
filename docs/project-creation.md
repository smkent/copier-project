---
title: Creating a project
icon: lucide/wand-sparkles
---

# Creating a new project

## Choose a template variant

See [Project variants](project-variants.md) for available project template
variants.

## Choose a project name

Project names must meet
[GitHub's repository name criteria][github-repository-name].

### Python project names

Python project names must meet the
[Python package name criteria][pyproject-name].

If you choose to [publish your project on PyPI][pypi], the project name will be
used as the package name (e.g. for `pip install`).

!!! tip
    If you plan to publish your project on PyPI, ensure:

    1. You have an [active PyPI account][pypi-login]
    2. Your desired package name is available!

## Create a GitHub repository

[Create a repository on GitHub for your new project][github-new].
Set **Repository name** to your chosen project name.

## Generate new project from template

1. In the directory where the new project should be created, run Copier:

    ```sh
    copier copy "gh:smkent/copier-python" ./project_name
    ```

    Copier will prompt for project information.
    Answer the prompts to configure your project.
    When complete, Copier will create your new project in `./project_name`.

2. Change to the new project directory:

    ```
    cd ./project_name
    ```

## Initialize the project

To complete project initialization, run:

```sh
mise run init
```

This will:

1. Create the local git repository
2. Install tools, dependencies, and git hooks (same as `mise install`)
3. Create an initial commit with the newly created project contents
4. Add your GitHub repository as the `origin` remote
   (when `project_visibility: public`)

## Push repository to GitHub

Push your new project to your GitHub repository:

```sh
git push -u origin main
```

Your project's contents should now be visible on GitHub!

[github-new]: https://github.com/new
[github-repository-name]: https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository
[pypi-login]: https://pypi.org/account/login/
[pypi]: https://pypi.org
[pyproject-name]: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#name
