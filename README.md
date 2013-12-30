# Customizer

Customizer is an advanced Live CD customization and remastering tool. With it, you can build own Ubuntu-based remix using Ubuntu Mini Remix, Ubuntu or its derivatives ISO image with a few mouse clicks.

##1 Dependencies:

This branch relies on Gambas 2 packages!

If you have 12.04 or a older releas skip the following and go to step 2.

If you have have newer version than 12.04 follow these steps:

Open your software-source(s) manager and add the repository:

    deb http://archive.ubuntu.com/ubuntu precise main universe

And update you software-source(s):
  
    sudo apt-get update

And now you can continue.

##2 Getting Started:

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

##3 Credits:

Ivailo Monev 'SmiL3y' (code developer) `xakepa10@gmail.com`

Michal Glowienka 'eloaders' (PPA maintainer) `eloaders@yahoo.com`

Mubiin Kimura 'clearkimura' (documentation) `clearkimura@gmail.com`

##4 Legal:

The GNU General Public License version 2 (GPLv2)

Copyright (C) 2010-2013 Ivailo Monev

Copyright (C) 2013 Mubiin Kimura
