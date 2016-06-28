**As January 2016, Customizer has been forked and is now being maintained at https://github.com/kamilion/customizer. For more details, see [issue #70](https://github.com/clearkimura/Customizer/issues/70). The existing repository is now considered as "old stable".**

### NAME

Customizer (formerly known as U-Customizer)


### SYNOPSIS

    customizer [-h] [-e] [-c] [-x] [-p] [-d] [-k] [-r] [-q] [-t] [-D] [-v]


### DESCRIPTION

Customizer is an advanced LiveCD customization and remastering tool. With it, you can build own
Ubuntu-based remix using Ubuntu Mini Remix, Ubuntu or its derivatives ISO image with a few mouse clicks.


### OPTIONS

    -h, --help       Show this help message and exit
    -e, --extract    Exctract ISO image
    -c, --chroot     Chroot into the filesystem
    -x, --xnest      Execute nested X-session
    -p, --pkgm       Execute package manager
    -d, --deb        Install Debian package
    -k, --hook       Execute hook
    -r, --rebuild    Rebuild the ISO image
    -q, --qemu       Test the builded image with QEMU
    -t, --clean      Clean all temporary files and folders
    -D, --debug      Enable debug messages
    -v, --version    Show Customizer version and exit


### ENVIRONMENT

    /etc/customizer.conf  -  configuration file
    <prefix>/share/customizer/exclude.list - files/dirs to exclude when compressing filesystem


### REQUIREMENTS

    make
    binutils
    gcc (g++)
    python (python2.7 and python2.7-dev)
    pyqt4 (python-qt4 and pyqt4-dev-tools)
    squashfs-tools (>=4.2)
    xorriso
    xhost (x11-xserver-utils)
    xephyr (xserver-xephyr)
    qemu (qemu-kvm)

On Ubuntu 12.04 or 14.04 release, do:
```sh
sudo apt-get install git build-essential fakeroot make binutils g++ \
 python python-dev python-qt4 pyqt4-dev-tools squashfs-tools \
 xorriso x11-xserver-utils xserver-xephyr qemu-kvm dpkg-dev \
 debhelper qt4-dev-tools qt4-linguist-tools \
 --no-install-recommends
```

### INSTALL AND RUN

    make && sudo make install
    # to run it: 
    sudo customizer -h # command line version
    sudo customizer-gui # GUI version

See our [first guide](https://github.com/clearkimura/Customizer/wiki/First-guide) to get you started.


### AUTHORS

Ivailo Monev 'SmiL3y' (code developer) `xakepa10@gmail.com`

Michal Glowienka 'eloaders' (PPA maintainer) `eloaders@yahoo.com`

Mubiin Kimura 'clearkimura' (documentation)


### BUGS REPORT

Create and submit your issue at https://github.com/fluxer/Customizer/issues

**IMPORTANT** You should include the following details: what version of system host, 
what version of customizer, what ISO image, description of problem, full output log that is 
not just the part of what you consider relevant, and if possible, relevant screenshots.

See our guideline on [issue submission](https://github.com/clearkimura/Customizer/wiki/Issue-submission).

The developers will look into submitted issues from time to time, usually a day or two.
Only issues found in latest versions of Customizer are concerned. Issues in older versions
will be ignored.


### COPYRIGHT

Copyright (C) 2010-2013 Ivailo Monev

Copyright (C) 2013-2015 Mubiin Kimura

License: GPLv2


### HISTORY

In late 2010, this project was registered on Sourceforge.net. Since November 2011,
documentation is contributed. As December 2011, Customizer development has moved to
GitHub and has been tested thoroughly on Ubuntu 10.04 (Lucid Lynx). One year later, 
as December 2012, Customizer stable release has hit 3.2.3.

Between late-2014 and early-2015, Customizer was rewritten in Python with the goal to 
support Ubuntu releases newer than 12.04 and making it more stable and robust.


### SEE ALSO

You can find more information about Customizer at https://github.com/fluxer/Customizer/wiki
