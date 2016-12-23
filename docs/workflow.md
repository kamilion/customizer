Understanding work flow
=======================

This is an essential guide for contributors who want to understand
work flow that supports this project. Before reading further,
contributors are expected to have some knowledge of [Git] and
[GitHub Flow].

Git or GitHub
-------------

When working on project that is hosted on GitHub, contributors have
choice to use either Git program or GitHub web service. GitHub web
service could do most of things that Git program can do. Therefore,
contributors might prefer to use GitHub web service for common tasks.

Except for uploading files to the repository, Git program may be
preferred. This becomes more apparent when making changes to multiple
files, as well as making changes to files that cannot be edited by
online text editor.

GitHub (since early 2016) can now upload files by drag-and-drop or by
using 'Upload files' button. This might be preferred by contributors
to upload files without making changes.

Direct commit or pull request
-----------------------------

For any given changes to be made, contributor has two options: direct
commit or pull request.

Contributor who has been granted permission to particular repository
(collaborator) can do direct commit. That is, commit will be visible
as soon as changes have been pushed to the repository.

Without the permission, contributor will usually create a fork, make
changes to the fork, then finally create a pull request from the
original repository to merge changes from fork to the repository.

The owner and collaborators of particular repository have both options
readily. Consider the following preferences.

* Direct commit is preferred for making individual changes to the
  existing files, creating new files (one file at a time, limited to
  text documents), and updating documentation and other simple tasks.

* Pull request is preferred for making multiple changes to multiple
  files that related to each other, creating new files (multiple files
  at a time), and making changes that require testing.

The `master` branch is always considered usable and shall not break
user experience. Therefore, it is much advisable to use pull request
for changes that require testing or that might introduce issues.

Commit title and description
----------------------------

When making direct commit or pull request, there are two text fields
that need to be filled: title and description (comment). Title will
contain some text that GitHub has prepared by default.

* For direct commit: when making changes to `FILENAME` the title will
  be set to 'Update FILENAME'.

* For pull request: when creating pull request prior to merge changes
  from `another` branch, the title is set to the name of branch and
  the result is 'Another (#ISSUE)'.

* When merging changes from other fork that has been created outside
  the original repository, the title will be set to something that
  looks like 'Merge pull request #ISSUE from USERNAME/master'.

Regardless of direct commit and pull request, the default title may be
changed to "something else" but GitHub will limit to 50 characters.

In any case, contributors are advised to use title with default text
as it is, for least hassles and keeping title to minimal. Description
can contain more details, including @mention and #issue for reference.

If contributor prefers to use Git program, use multiple `-m` options
so that first part of message becomes the title (keep this short and
minimal) and following part of message becomes the description as
separate paragraphs.

Example commit using Git program:

```
$ git commit -m "Add test.txt" -m "Test description"
[master 73e0500] Add test.txt
 1 file changed, 1 insertion(+)
 create mode 100644 test.txt

$ git log
commit 73e050032a1b908e5037aea713b959859660ed8c
Author: username <example@email.com>
Date:   Fri Dec 16 03:48:46 2016 +0800

    Add test.txt
    
    Test description

$ git log --oneline
73e0500 Add test.txt
bd0c70c ...
```

Interim work flow
-----------------

The following output from `git` command is real commit history that
more or less follows above guide, and that shall demonstrate work flow
adopted by the interim maintainer.

> To be updated

Future work flow
----------------

> To be updated

[Git]: https://git-scm.com/
[GitHub Flow]: https://guides.github.com/introduction/flow/
