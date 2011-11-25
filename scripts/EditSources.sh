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
set -u
source /opt/Customizer/Functions.sh
source /opt/Customizer/settings.conf
Reset='\e[0m'
Red='\e[1;31m'
Green='\e[1;32m'
Yellow='\e[1;33m'

echo -e "${Yellow}#${Reset} ${Green}Checking${Reset}"
check_fs_dir
check_sources_list

echo -e "${Yellow}#${Reset} ${Green}Editing sources.list with: ${Yellow}$EDITOR${Reset}"
if [ ! -r "$WORK_DIR/FileSystem/etc/apt/sources.list" ];then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}The sources.list file isn't readable${Reset}"
	read nada
	exit
fi

if [ ! -w "$WORK_DIR/FileSystem/etc/apt/sources.list" ];then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}The sources.list file isn't writable${Reset}"
	read nada
	exit
fi

$EDITOR "$WORK_DIR/FileSystem/etc/apt/sources.list" 2> /dev/null || { echo -ne "${Red}ERROR${Reset}: ${Yellow}An error accure while trying to open the file.${Reset}"; read nada; exit; }
