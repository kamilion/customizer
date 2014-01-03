# Customizer

Customizer is an advanced Live CD customization and remastering tool. With it, you can build own Ubuntu-based remix using Ubuntu Mini Remix, Ubuntu or its derivatives ISO image with a few mouse clicks.

This branch relies on Gambas 2 packages, optimized for 12.04 and older releases.

**IMPORTANT** You need to enable some repositories to install the dependencies and `gambas2` packages. Ensure that you have enabled the **universe** repository in the Software Sources. Then, update the repository (or open Terminal and run `sudo apt-get update`) and follow the instructions below.

## Getting Started

Download installation script and execute:

    wget https://dl.dropboxusercontent.com/u/54183088/install.sh
    chmod +x install.sh
    sudo ./install.sh -i

Then, run Customizer in CLI:

    sudo /opt/Customizer/CLI.sh -h

Or, run Customizer in GUI:

    gksu /opt/Customizer/GUI.gambas

**IMPORTANT** If you are using KDE, replace `gksu` with `kdesu` or `kdesudo`.

Visit our GitHub Wiki at  https://github.com/clearkimura/Customizer/wiki  for details.

## Credits

Ivailo Monev 'SmiL3y' (code developer) `xakepa10@gmail.com`

Michal Glowienka 'eloaders' (PPA maintainer) `eloaders@yahoo.com`

Mubiin Kimura 'clearkimura' (documentation) `clearkimura@gmail.com`

Andrie Vorster 'andries-petrus-vorster' (README.md)

Ayman 'aymanim' (typo, spellcheck)

## Legal

The GNU General Public License version 2 (GPLv2)

Copyright (C) 2010-2013 Ivailo Monev

Copyright (C) 2013 Mubiin Kimura
