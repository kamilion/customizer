### NAME

customizer - advanced Live CD/DVD remastering tool

	
### SYNOPSIS

    /opt/Customizer/CLI.sh [OPTION] [ARGUMENT]


### DESCRIPTION

Looking for a tool that will allow you to customize Ubuntu, Kubuntu, Lubuntu, Xubuntu,
Linux Mint or other Ubuntu based ISO images? Well, you've found it! Customizer allows
you to customize them the way you want, within few minutes (on a modern PC), running 
Terminal, Synaptic, Desktop session (in chroot environment) and even more so you can
modify the images to fit your needs.


### OPTIONS

    -e,   --extract   Exctract ISO image
    -c,   --chroot    Chroot into the filesystem
    -x,   --xnest     Execute nested X-session
    -p,   --pkgm      Execute package manager
    -d,   --deb       Install Debian package
    -k,   --hook      Execute hook
    -g,   --gui       Install GUI (DE/WM)
    -r,   --rebuild   Rebuild the ISO image
    -q,   --qemu      Test the builded image with QEMU
    -t,   --clean     Clean all temporary files and folders
    -h,   --help      Display this message
    -v,   --version   Show the current version and more


### ENVIRONMENT

    /opt/Customizer                -  Customizer's location
    /opt/Customizer/settings.conf  -  configuration file


### REQUIREMENTS

Core dependencies are:

    coreutils
    sed
    grep
    rsync
    squashfs-tools (>=4.2)
    genisoimage

GUI dependencies are:

    dbus
    xephyr
    qemu
    imagemagick
    gambas2-gui | gambas3-gb-gui
    gambas2-form | gambas3-gb-form
    gambas2-runtime | gambas3-runtime


### INSTALL AND RUN

This is how you can download and install using script from Terminal.

    wget https://github.com/downloads/fluxer/Customizer/install.sh
    chmod +x install.sh
    sudo ./install.sh -i

This is how you can run Customizer from program launcher or Terminal

    su-to-root -X -c /opt/Customizer/GUI.gambas

For alternative methods or more details, refer to the official user guides at https://github.com/fluxer/Customizer/wiki

    
### AUTHORS

Ivailo Monev 'SmiL3y' (code developer) `xakepa10@gmail.com`

Michal Glowienka 'eloaders' (PPA maintainer) `eloaders@yahoo.com`

Mubiin Kimura 'clearkimura' (documentation) `clearkimura@gmail.com`


### BUGS

To report a bug, you should include the following details: what version of system host, 
what version of customizer, what ISO image, description of problem and screenshot, if possible.
The developers will look into submitted issues from time to time, usually a day or two.
Only issues found in latest versions of Customizer are concerned. Issues in older versions will
be ignored.

Example of issue submission details:

    Ubuntu 12.04, Customizer 3.2.1, ubuntu-mini-remix-12.04-amd64. Using GUI, after select 'Build',
    cannot create ISO image file, Terminal shows Error 119: No kernel found when compiling image.

Create and submit your issue at https://github.com/fluxer/Customizer/issues


### COPYRIGHT
    
Copyright (C) 2010-2012  Ivailo Monev

License: GPLv2


### HISTORY

In late 2010, this project was registered on Sourceforge.net. Since November 2011,
documentation is contributed. As December 2011, Customizer development has moved to
GitHub and has been tested thoroughly on Ubuntu 10.04(Lucid Lynx). Presently
maintained for compatibility fixes and documentation.

View latest changes at https://github.com/fluxer/Customizer/wiki/Changes-log


### SEE ALSO

PPA stable at https://launchpad.net/~customizer-dev-team/+archive/stable

PPA devel at https://launchpad.net/~customizer-dev-team/+archive/devel

You can find more information about Customizer at https://github.com/fluxer/Customizer/wiki