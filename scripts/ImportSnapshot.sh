#!/usr/bin/env bash
#
# This script is part of Customzier
#
# Homepage: https://github.com/fluxer/Customizer
# Wiki: https://github.com/fluxer/Customizer/wiki
# Issues: https://github.com/fluxer/Customizer/issues
#
# C0diNg: Ivailo Monev (a.k.a SmiL3y) <xakepa10@gmail.com> 
#
set -u
source /opt/Customizer/Functions.sh
source /opt/Customizer/settings.conf
Reset='\e[0m'
Red='\e[1;31m'
Green='\e[1;32m'
Yellow='\e[1;33m'

echo -e "${Yellow}#${Reset} ${Green}Checking${Reset}"
if [ ! -e "$SNAPSHOT" ];then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}The snapshot doesn't exists.${Reset}"
	read nada
	exit
fi

check_lock

case "$SNAPSHOT" in
	*.cps) true ;;
	*) echo -ne "${Red}ERROR${Reset}: ${Yellow}This is not Customizer project snapshot.${Reset}"; read nada; exit ;;
esac

if [ -d "$WORK_DIR/FileSystem" ] || [ -d "$WORK_DIR/ISO" ]; then
	recursive_umount
	echo -e "${Yellow}#${Reset} ${Green}Cleaning up${Reset}"
	rm -rf "$WORK_DIR/FileSystem"
	rm -rf "$WORK_DIR/ISO"
fi

mkdir -p "$WORK_DIR"
cd "$WORK_DIR"
echo -e "${Yellow}#${Reset} ${Green}De-Compressing snapshot${Reset}"
tar -axf "$SNAPSHOT" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}An error accure while trying to decompress the snapshot${Reset}"; read nada; exit; }

echo -e "   ${Yellow}*${Reset} ${Green}De-Compressing root filesystem${Reset}"
tar -axf rootfs.* || { echo -ne "${Red}ERROR${Reset}: ${Yellow}An error accure while trying to de-compress the root filesystem${Reset}"; read nada; exit; }

echo -e "   ${Yellow}*${Reset} ${Green}De-Compressing ISO folder${Reset}"
tar -axf isofolder.* || { echo -ne "${Red}ERROR${Reset}: ${Yellow}An error accure while trying to de-compress the ISO folder${Reset}"; read nada; exit; }

echo -e "${Yellow}#${Reset} ${Green}Deleting temp files${Reset}"
rm -rf rootfs.* isofolder.*
