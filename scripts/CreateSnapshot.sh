#!/bin/bash
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
# source /opt/Customizer/ProgressBar.sh
Reset='\e[0m'
Red='\e[1;31m'
Green='\e[1;32m'
Yellow='\e[1;33m'

if [ -d "/tmp/snapshot" ];then
	echo -e "${Yellow}#${Reset} ${Green}Deleting what had been left from previous attempts${Reset}"
	rm -rf /tmp/snapshot
	mkdir /tmp/snapshot
else
	mkdir /tmp/snapshot
fi

echo -e "${Yellow}#${Reset} ${Green}Compressing the root filesystem${Reset}"
tar -cjf /tmp/snapshot/rootfs.tar.bz2 "$WORK_DIR/FileSystem" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}An error accure while trying to compress the root filesystem.${Reset}"; read nada; exit; }

echo -e "${Yellow}#${Reset} ${Green}Compressing the ISO folder${Reset}"
tar -cjf /tmp/snapshot/isofolder.tar.bz2 "$WORK_DIR/ISO" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}An error accure while trying to compress the ISO folder.${Reset}"; read nada; exit; }

echo -e "${Yellow}#${Reset} ${Green}Putting it all together${Reset}"
SN="$WORK_DIR/snapshot-`date +%H-%M-%S`.cps"
tar -cf $SN /tmp/snapshot || { echo -ne "${Red}ERROR${Reset}: ${Yellow}An error accure while trying to combine the two compressed archives.${Reset}"; read nada; exit; }
rm -rf /tmp/snapshot

echo -e "${Yellow}#${Reset} ${Green}Snapshot successfuly created${Reset}: ${Yellow}SN${Reset}"
read nada
exit