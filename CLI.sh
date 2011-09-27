#!/bin/bash -u
#
# This script is part of Customzier
#
# Homepage: http://u-customizer.sf.net
# Forum: https://sourceforge.net/apps/phpbb/u-customizer
#
# C0diNg: Ivailo Monev (a.k.a SmiL3y)
#
# E-Mail: xakepa10@gmail.com
# Jabber: xakepa@jabber.org
# Skype: big-smoke10
#

set -e
source /opt/Customizer/Functions.sh
source /opt/Customizer/settings.conf
Reset='\e[0m'
Red='\e[1;31m'
Green='\e[1;32m'
Yellow='\e[1;33m'

Usage () {
echo "
 Main options:
     -u   Exctract ISO image
     -c   Chroot into the filesystem
     -x   Execute nested X-session
     -e   Edit sources.list
     -a   Execute package manager
     -d   Install Debian package
     -k   Execute hook
     -g   Install GUI (DE/WM)
     -s   Creates snapshot of your current work
     -i   Imports created snapshot
     -r   Rebuild the ISO image
     -q   Test the builded image with QEMU
     -t   Clean all temporary files and folders

 Other options:
     -h   Display this message
     -w   Check for new version
     -v   Show the current version and more
"
}

Version () {
echo
echo "Customizer v3.0.5

Homepage: http://u-customizer.sf.net
Forum: https://sourceforge.net/apps/phpbb/u-customizer


Main developer: Ivailo Monev (a.k.a SmiL3y)
<xakepa10@gmail.com>

PPA maintainer:
Michał Głowienka (a.k.a. eloaders)
<eloaders@yahoo.com>"
echo
}

while getopts "ucxeadkgsirqthwv" opt; do
case $opt in
	u) su-to-root -c /opt/Customizer/scripts/Use.sh ;;
	c) su-to-root -c /opt/Customizer/scripts/Chroot.sh ;;
	x) su-to-root -c /opt/Customizer/scripts/Xnest.sh ;;
	e) su-to-root -c /opt/Customizer/scripts/EditSources.sh ;;
	a) su-to-root -c /opt/Customizer/scripts/Archive.sh ;;
	d) su-to-root -c /opt/Customizer/scripts/InstallDEB.sh ;;
	k) su-to-root -c /opt/Customizer/scripts/Hook.sh ;;
	g) su-to-root -c /opt/Customizer/scripts/InstallGUI.sh ;;
	s) su-to-root -c /opt/Customizer/scripts/CreateSnapshot.sh ;;
	i) su-to-root -c /opt/Customizer/scripts/ImportSnapshot.sh ;;
	r) su-to-root -c /opt/Customizer/scripts/Build.sh ;;
	q) su-to-root -c /opt/Customizer/scripts/QEMU.sh ;;
	t) su-to-root -c /opt/Customizer/scripts/Clean.sh ;;
	w) /opt/Customizer/scripts/Update.sh ;;
	v) Version ;;
	h) Usage ;;
	*) echo -e "${Red}ERROR${Reset}: ${Yellow}Unrecognized argument${Reset}" ;;
esac
done
	
