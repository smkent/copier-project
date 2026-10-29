---
title: Development workflow
icon: lucide/braces
---

# copier-project development workflow

## Cloning the repository

```sh
git clone https://github.com/smkent/copier-project
cd copier-project
```

Run `mise install` in new repository clones to install tools, dependencies, and
git hooks:

```sh
mise install
```

## Local template usage

While making development changes to copier-project, the local template can be
used to create projects. To do so, run `copier copy` with the `-r`/`--vcs-ref`
argument:

```sh
copier copy -r HEAD path/to/copier-project/clone/ path/to/new/project/
```

This will render the new project from the current template state including
uncommitted changes.

## Development tools

* `mise run lint`: Run formatters and static checks
* `mise run test`: Run tests

The `lint` and `test` tasks can also be run as a single combined command with:

```sh
mise run lt
```

### Test snapshots

Many copier-project tests compare template-rendered files with saved snapshots.
When templates are modified, the snapshots need to be updated. Update test
snapshots by running:

```sh
mise run snapup
```

## Documentation server

Start the development server with:

```sh
mise run docs
```

The documentation site will be served at:

[**http://localhost:8000**](http://localhost:8000){ .md-button .md-button--primary target="_blank" }

To use a different bind host/port, run `mise run docs --help` for usage info.
