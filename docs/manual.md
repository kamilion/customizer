### NAME

Customizer (formerly U-Customizer)


### SYNOPSIS

    customizer [-h] [-e] [-c] [-x] [-p] [-d] [-k] [-r] [-q] [-t] [-D] [-v]


### DESCRIPTION

Customizer, formerly known as U-Customizer, is an advanced Live CD
customization and remastering tool. Use any supported Ubuntu-based ISO
image, such as Ubuntu Mini Remix, Ubuntu or its derivatives ISO image
to build your own remix or custom ISO image with a few mouse clicks.


### OPTIONS

    -h, --help     show this help message and exit
    -e, --extract  Extract ISO image
    -c, --chroot   Chroot into the filesystem
    -x, --xnest    Execute nested X-session
    -p, --pkgm     Execute package manager
    -d, --deb      Install Debian package
    -k, --hook     Execute hook
    -r, --rebuild  Rebuild the ISO image
    -q, --qemu     Test the built ISO image with QEMU
    -t, --clean    Clean all temporary files and folders
    -D, --debug    Enable debug messages
    -v, --version  Show Customizer version and exit

These options do not require additional arguments. There is a need to
edit the configuration file before using some options, which are
`-e, --extract`, `-d, --deb` and `-k, --hook` in particular.


### ENVIRONMENT

    /etc/customizer.conf
        configuration file

    $(PREFIX)/share/customizer/exclude.list
        files/dirs to exclude when compressing filesystem

In Ubuntu and Debian, `$(PREFIX)` refers to `/usr`, which is obtained
from `python2-config --prefix` command. Other systems may use unique
prefix instead of that.


### REQUIREMENTS

    GNU Make (make)
    GNU Binary tools (binutils)
    GNU Compiler Collection (gcc)
    GNU C++ compiler (g++)
    Python (py27|python>=2.7)
    PyQt4 (py-qt4*|pyqt4*,qt4*)
    SquashFS tools (squashfs-tools>=4.2)
    GNU xorriso (xorriso)
    Xhost (xhost|x11-xserver-utils)
    Xephyr (xephyr|xserver-xephyr)
    Qemu (qemu|qemu-kvm)

In Ubuntu and Debian, some components are provided by meta packages or
otherwise may be provided by individual packages. Other systems may
not require some components such as `g++`.


### INSTALL AND RUN

    make && sudo make install

    sudo customizer -h
        command line interface

    sudo customizer-gui
        graphical user interface

In Ubuntu and Debian, application shortcut is provided to run the
program using pkexec authentication instead of sudo. Other systems
may not utilize the shortcut or may not support pkexec.


### AUTHORS

    Ivailo Monev 'fluxer/SmiL3y'
        Code developer

    Michal Glowienka 'eloaders'
        PPA maintainer

    Mubiin Kimura 'clearkimura'
        Documentation, Interim maintainer

    Graham Cantin 'Kamilion'
        Fork maintainer


### REPORTING BUGS

Create a new issue on GitHub. Make sure to review the guidelines for
contributing before proceeding to submit new issue.


### COPYRIGHT

Customizer is copyright by Ivailo Monev, et al.


### SEE ALSO

[First guide] to get you started.

[debian/control] file for requirements to build and compile package
in Ubuntu and Debian.

[debian/copyright] file for copyright text and license, including
history of development and ownership.

[graphs/contributors] on GitHub for commits history.

[data/contributors] file that contains full listing.

[contributing] file that contains guidelines for contributing.

[Wiki] for more information.


[First guide]: /../../wiki/First-guide
[debian/control]: ../../master/debian/control
[debian/copyright]: ../../master/debian/copyright
[graphs/contributors]: /../../graphs/contributors
[data/contributors]: ../../master/data/contributors
[contributing]: ../../master/CONTRIBUTING.md
[Wiki]: /../../wiki
