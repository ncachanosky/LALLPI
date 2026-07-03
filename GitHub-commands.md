# GitHub Commands — Quick Reference

A personal cheat sheet for committing and pushing changes to the LALLPI
repo from Positron's terminal, instead of GitHub Desktop. Every command
here is typed directly into the terminal panel and confirmed with Enter.

## The concepts, briefly

Three states matter day to day:

1. **Working directory** — the actual files on your computer, as you've
   edited them. Git notices when these differ from the last commit, but
   doesn't track them yet.
2. **Staged** — files you've explicitly told Git "include this in the
   next commit." This is a deliberate middle step -- you can edit five
   files but only stage and commit two of them if you want.
3. **Committed** — a permanent snapshot in your local repo's history,
   with a message describing what changed. Not yet on GitHub until you
   **push**.

The everyday flow is: edit files -> **stage** them -> **commit** them ->
**push** them to GitHub.

## The everyday workflow

Run these in order, every time you've made changes you want to save to
GitHub. This is the sequence you'll use almost every session.

### 1. Check what's changed

```bash
git status
```

Shows which files you've modified, which are staged, and which Git
doesn't know about yet. Always worth running this first -- it's how you
confirm Git sees the changes you expect, and it's the single most useful
command for figuring out "did my edit actually get picked up." Nothing
here is destructive; you can run this as often as you like.

### 2. Stage your changes

```bash
git add .
```

Stages *everything* that's changed in the current folder and its
subfolders -- the `.` means "here and below." This is the simplest option
and fine for this project's normal workflow.

To stage only specific files instead:

```bash
git add _quarto.yml pages/data.qmd
```

List as many filenames as you want, separated by spaces.

### 3. Commit the staged changes

```bash
git commit -m "Fix country count on Data page"
```

Creates the actual snapshot, with `-m` followed by a short message in
quotes describing what changed. Write something specific enough that you
(or a collaborator) can understand it later just from `git log` -- "fix
bug" is technically valid but useless in six months; "Fix country count
on Data page" tells you something.

### 4. Push to GitHub

```bash
git push
```

Uploads your committed changes to GitHub. This is the step that actually
makes them visible on github.com and triggers a new Netlify deploy --
`git commit` alone only saves the snapshot *locally*, on your own
machine. If you've ever wondered why a change "should be there" but isn't
showing up on the live site, checking whether you actually ran `git push`
(not just `git commit`) is the first thing to check.

## Checking things before and after

### See exactly what changed, line by line

```bash
git diff
```

Shows the actual added/removed lines for everything modified but not yet
staged. Useful to review before staging, especially after Claude delivers
a file and you want to see precisely what's different from what you had.

```bash
git diff --staged
```

Same idea, but for changes you've already staged with `git add` -- this
is your last look before committing.

### See your commit history

```bash
git log
```

Lists past commits, newest first, with their messages, authors, and
dates. Press `q` to exit this view (it opens in a scrollable pager).

```bash
git log --oneline
```

Same thing, condensed to one line per commit -- faster to scan.

### Confirm a specific file's current committed state

```bash
git show HEAD:path/to/file.qmd
```

Prints exactly what's actually committed for that file right now, e.g.
`git show HEAD:_quarto.yml`. This is the most reliable way to answer "is
this fix actually in the repo" without relying on what your editor
happens to have open, since your editor could be showing an unsaved or
uncommitted version.

## Getting the latest changes

```bash
git pull
```

Downloads and merges any changes from GitHub into your local copy. Worth
running at the *start* of a session if there's any chance the GitHub
version has changed since you last worked locally (e.g., you edited
something directly on github.com, or from a different machine).

## If you need to undo something

```bash
git restore path/to/file.qmd
```

Discards uncommitted changes to that file, reverting it back to the last
commit. Only works for changes that haven't been staged yet.

```bash
git restore --staged path/to/file.qmd
```

Unstages a file (moves it from "staged" back to just "modified") without
discarding the actual edits -- useful if you ran `git add .` but decided
you don't want to commit one particular file yet.

## A minimal real session, start to finish

```bash
git status
git add .
git commit -m "Add codebook page and fix country count"
git push
```

That's the whole loop. Everything else in this file is either
troubleshooting or things you'll reach for occasionally, not every time.

## Further reference

GitHub's own official cheat sheet, for anything not covered here:
https://docs.github.com/en/get-started/git-basics/git-cheatsheet