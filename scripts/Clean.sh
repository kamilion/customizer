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
source /opt/Customizer/Functions.sh
source /opt/Customizer/settings.conf
Reset='\e[0m'
Red='\e[1;31m'
Green='\e[1;32m'
Yellow='\e[1;33m'

if [ -d "$WORK_DIR/FileSystem" ] || [ -d "$WORK_DIR/ISO" ];then
	recursive_umount
	echo -e "${Yellow}#${Reset} ${Green}Deleting FileSystem folder${Reset}"
	rm -rf "$WORK_DIR/FileSystem"
	echo -e "${Yellow}#${Reset} ${Green}Deleting up ISO folder${Reset}"
	rm -rf "$WORK_DIR/ISO"
else
	echo -e "${Yellow}#${Reset} ${Green}There is nothing to clean${Reset}"
fi
	
	
