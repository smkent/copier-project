---
title: Template updates
icon: lucide/git-merge
---

# Applying copier-project template updates

**copier-project is managed by its own template!**
When the template changes, copier-project itself can be updated with:

```sh
copier update
```

This will repeat the setup prompts, in case any prompts have been added or
changed.

To apply updates without being prompted (reusing all previous answers), run:

```sh
copier update -l
```

When [`copier update`][copier-update] is finished, view changes with
`git status` and `git diff`. Resolve any conflicts, and then commit the result.

[copier-update]: https://copier.readthedocs.io/en/stable/updating/
