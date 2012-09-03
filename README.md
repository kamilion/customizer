## NAME

customizer - Advanced Live CD/DVD remastering tool

	
	
## SYNOPSIS

> /opt/Customizer/CLI.sh \[OPTION\] ...



## DESCRIPTION

Looking for a tool that will allow You to customize Ubuntu, Kubuntu, Lubuntu, Xubuntu ,
Linux Mint or  other Ubuntu based ISO images? Well, you've found it! Customizer is the
right choise - it allows you to customize them the way you want to within the matter of
few minutes (on a modern PC) running Terminal, Synaptic, Desktop session (in chroot
environment) and even more so you can modify the images to fit your needs.

	
	
## OPTIONS

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



## ENVIRONMENT

### Configuration file
> /opt/Customizer/settings.conf 

## REQUIREMENTS

### Core dependencies
> coreutils

> sed

> grep

> rsync

> squashfs-tools => 4.2

> genisoimage

### GUI dependencies

> dbus

> xephyr

> qemu

> imagemagick

> gambas2-gui

> gambas2-form

> gambas2-runtime



## AUTHORS

### Coding
> Ivailo Monev (a.k.a SmiL3y) `xakepa10@gmail.com`
    
### PPA maintainer
> Michal Glowienka (a.k.a. eloaders) `eloaders@yahoo.com`
    
### Documentation
> Mubiin Kimura (a.k.a. clearkimura) `clearkimura@gmail.com`



## REPORTING BUGS

To report a bug, create and submit your issue on [this page] (https://github.com/fluxer/Customizer/issues). The developers will look
into submitted issues from time to time, usually a day or two. Only issues found in
latest versions of Customizer are concerned. Therefore, issues in older versions will
be ignored.



## COPYRIGHT
    
Copyright (C) 2010-2012  Ivailo Monev

License: GPLv2



## HISTORY

In late 2010, this project was [registered on Sourceforge.net](http://sourceforge.net/projects/u-customizer/). Since November 2011,
documentation is contributed. As December 2011, Customizer development has moved to
GitHub, maintained up to version 3.1.1, has been tested thoroughly on Ubuntu 10.04
(Lucid Lynx). Presently maintained for compatibility fixes and documentation. Latest
changes made to Customizer is found under [this log](https://github.com/fluxer/Customizer/wiki/Changes-log).



## SEE ALSO

### Customizer in action
> [Screenshots of version 3.2.x](https://docs.google.com/drawings/d/1-XP1LZFIPF0kT1Toet1tGOks27qPqC488NHasmQHVuU/edit), uploaded by clearkimura.


> [First screencast HD-1024p OGV, 104MB](http://dl.dropbox.com/u/54183088/out-4.ogv), uploaded by smil3y.

> [First screencast SD-480p MPG, 65MB](http://dl.dropbox.com/u/54183088/out-4_small_size.mpg), uploaded by smil3y, decoded by clearkimura.

### Customizer official user guides

> [Quick Guide 1: How to Install Customizer](https://docs.google.com/document/d/1MF-GZYX90E4JKHGtnAKK3LHFYVV3ArC641QFOr3lgNU/edit) on Google Docs, shared by clearkimura.

> [Quick Guide 2: How to Setup Customizer](https://docs.google.com/document/d/149ug1YfiO-6OiCUqa9XTI1E1HjEYRKRkQZ4QTa54BW8/edit) on Google Docs, shared by clearkimura.

> Quick Guide 3: How to Use Customizer ---*planning


> [Full user guide](https://docs.google.com/document/d/1PfhHnSBjv-IDI7Yh5obhMGYCAV9Gw1NPEynU4GqKTsA/edit) on Google Docs, shared by clearkimura.

> [Old user guide](http://sourceforge.net/apps/phpbb/u-customizer/viewtopic.php?f=1&t=10&start=0) on Sourceforge Forum. Obsolete.

### Notable mentions

> 2012.07.03 -- Customizer 3.3.0 is listed by [Gaurav Joshi](http://alllinuxstuff.blogspot.com/2012/07/five-tools-to-build-your-own-ubuntu.html) as one of tools to build your own Ubuntu based distribution

> 2012.06.08 -- Customizer 3.2.2 review in Indonesian by [amrinz](http://www.berugak.com/komputer/linux/remastering-ubuntu-dengan-customizer.html)

> 2012.01.01 -- Customizer 3.1.1 review in Indonesian by [WAHYU AGUNG](http://www.linuk.web.id/2012/01/customize-ubuntu-based-livecd-dengan.html)

> 2011.12.17 -- Customizer 3.0.7 review in Indonesian by [WAHYU AGUNG](http://www.linuk.web.id/2011/12/customizer-advanced-livecd.html)

> 2011.11.14 -- Customizer is mentioned by [kapitanluffy](http://askubuntu.com/questions/79089/minimal-ubuntu-remastering) on askubuntu.com

> 2011.11.01 -- Customizer is featured in [Ubuntu User magazine issue 11](http://www.ubuntu-user.com/Magazine/Archive/2011/11), reported via [Ubuntu forums](http://ubuntuforums.org/showthread.php?p=11414452#post11414452).

The featured article, "Ubuntu Remastering: Make your own Ubuntu with Customizer", is not available as sample article at Ubuntu User magazine site. Community may contribute scanned copy, if any.

* 2011.08.21 -- Customizer is suggested by [Saptarshi Ghosh](https://answers.launchpad.net/ubuntu/+source/software-center/+question/168651) in Ubuntu Launchpad

* 2011.07.12 -- Customizer naming and logo discussion on [hikarilabs forum](http://hikarilabs.forumcommunity.net/?t=42321393&st=150)

* 2011.05.15 -- Customizer 2.2.0 review by [shiliarr95z](http://shiliarr95z.weebly.com/2/post/2011/05/using-u-customizer-remixing-ubuntu-mini-remix-1104.html)

* 2010.10.15 -- Earliest mention of Customizer is found under [this thread](http://ubuntuforums.org/showthread.php?t=1597825) on Ubuntu Forums.