#!/usr/bin/env bash
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

     -u|--use       Exctract ISO image
     -c|--chroot    Chroot into the filesystem
     -x|--xnest     Execute nested X-session
     -e|--sources   Edit sources.list
     -a|--archive   Execute package manager
     -d|--deb       Install Debian package
     -k|--hook      Execute hook
     -g|--gui       Install GUI (DE/WM)
     -s|--snapshot  Creates snapshot of your current work
     -i|--import    Imports created snapshot
     -r|--rebuild   Rebuild the ISO image
     -q|--qemu      Test the builded image with QEMU
     -t|--clean     Clean all temporary files and folders

 Other options:
     -h|--help      Display this message
     -v|--version   Show the current version and more
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

if [ "$#" != "0" ];then
	for arg in "$@"; do
		case $arg in
			-u|--use) su-to-root -c /opt/Customizer/scripts/Use.sh ;;
			-c|--chroot) su-to-root -c /opt/Customizer/scripts/Chroot.sh ;;
			-x|--xnest) su-to-root -c /opt/Customizer/scripts/Xnest.sh ;;
			-e|--sources) su-to-root -c /opt/Customizer/scripts/EditSources.sh ;;
			-a|--archive) su-to-root -c /opt/Customizer/scripts/Archive.sh ;;
			-d|--deb) su-to-root -c /opt/Customizer/scripts/InstallDEB.sh ;;
			-k|--hook) su-to-root -c /opt/Customizer/scripts/Hook.sh ;;
			-g|--gui) su-to-root -c /opt/Customizer/scripts/InstallGUI.sh ;;
			-s|--snapshot) su-to-root -c /opt/Customizer/scripts/CreateSnapshot.sh ;;
			-i|--import) su-to-root -c /opt/Customizer/scripts/ImportSnapshot.sh ;;
			-r|--rebuild) su-to-root -c /opt/Customizer/scripts/Build.sh ;;
			-q|--qemu) su-to-root -c /opt/Customizer/scripts/QEMU.sh ;;
			-t|--clean) su-to-root -c /opt/Customizer/scripts/Clean.sh ;;
			-v|--version) Version ;;
			-h|--help) Usage ;;
			*) echo -e "${Red}ERROR${Reset}: ${Yellow}Unrecognized argument${Reset}: ${Green}$arg${Reset}" ;;
		esac
	done
else
	Usage
fi
	
