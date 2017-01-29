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
  be set to something similar as the following.

      'Update FILENAME'

* For pull request: when merging changes from other fork that has
  been created outside the original repository, the title will be set
  to something similar as the following.

      'Merge pull request #ISSUE from USERNAME/master'
  
* However, when merging changes from `another` branch using "squash
  and merge" option, the title is set to the name of branch and the
  result is similar to the following.

      'Another (#ISSUE)'

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


Interim work flow
-----------------

The following output from `git` command is real commit history that
more or less follows above guide, and that shall demonstrate work flow
adopted by the interim maintainer.

    $ git log --oneline --decorate --graph --all
    * 917dde6 (HEAD, tag: 4.1.4-0, origin/master, origin/HEAD, master)
    Update CHANGELOG
    * 2815f71 Update Makefile
    * f5a4238 Update changelog
    * e0334d5 Fix141 (#151)
    * 670d2e8 Update workflow.md
    *   a9b0c0e Merge pull request #150 from clearkimura/fix148
    |\  
    | * d077914 Update Makefile
    | * ba9fbf2 Update Makefile
    | * a7aa170 Update customizer.policy.in
    | * 9ab23f6 Update changelog
    | * df72ba5 Update postrm
    | * 549d12d Update postinst
    | * 24034c8 Update control
    | * 33bb59e Update icons.file
    | * 8de9eee Add files via upload
    | * 5c3a464 Create icons.file
    |/  
    * c834df7 Update INSTALL
    * 939ebaa Update CONTRIBUTING.md
    * 728f723 Update workflow.md
    * c6ac94e Update workflow.md
    * f86b4df Update customizer.desktop.in
    * bfa514e Update qemu.py
    * bd0c70c Update workflow.md
    * f756bc7 Update README.md
    * 390f089 Update manual.md
    * 0a3bdd1 Update manual.md
    * 5bb10a9 Update INSTALL
    * d2d337f Update INSTALL
    * fb564c2 Update INSTALL
    * cafcc8b Update INSTALL
    * 944e4fd Update INSTALL
    * 854f824 Update changelog
    * 4b10294 Update control
    * 7943813 Update changelog
    * 1805d6d Update gui.py.in
    * 151688e Update main.py.in
    * 4f60523 Update control
    * 02cfc98 Update README.md
    * a686dd7 Update CHANGELOG
    * 291e9b3 Update CHANGELOG
    * 7b43830 Update README.md
    * e760c69 Create CONTRIBUTING.md
    * 19bdc59 Update Makefile
    * 0d33d0c Update copyright
    * 46b79e2 Update INSTALL
    * e87d6ac Update README.md
    * dc58d79 Rename Contributors to data/contributors
    * 85b14fd Create workflow.md
    * 521f544 Update Makefile
    * f3efc5d Update README.md
    * 956bd13 Create INSTALL
    * 9b7e0ea (tag: 4.1.3-0) Update CHANGELOG
    * 228049f Pre413 (#139)

Future work flow
----------------

This document was intended to be useful for beginning contributors.
Future work flow shall be decided by future contributors who have
relevant experience to decide work flow that suits this project.

[Git]: https://git-scm.com/
[GitHub Flow]: https://guides.github.com/introduction/flow/
