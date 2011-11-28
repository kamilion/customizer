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
check_lock
check_fs_dir

case "$COMPRESSION" in
	bzip2) COMPRESSION_OPTIONS="tar -cjf"; EXT="tar.bz2"; echo -e "   ${Yellow}*${Reset} ${Green}Using compression${Reset}: ${Yellow}$COMPRESSION${Reset}" ;;
	gzip) COMPRESSION_OPTIONS="tar -czf"; EXT="gz";echo -e "   ${Yellow}*${Reset} ${Green}Using compression${Reset}: ${Yellow}$COMPRESSION${Reset}" ;;
	tar) COMPRESSION_OPTIONS="tar -cf"; EXT="tar";echo -e "   ${Yellow}*${Reset} ${Green}Using compression${Reset}: ${Yellow}$COMPRESSION${Reset}" ;;
	*) echo -ne "${Red}ERROR${Reset}: ${Yellow}Invalid compression format specified${Reset}"; read nada; exit ;;
esac

if [ -d "/tmp/snapshot" ];then
	echo -e "${Yellow}#${Reset} ${Green}Deleting what had been left from previous attempts${Reset}"
	rm -rf /tmp/snapshot
fi

mkdir -p /tmp/snapshot
cd "$WORK_DIR"
echo -e "${Yellow}#${Reset} ${Green}Compressing the root filesystem${Reset}"
$COMPRESSION_OPTIONS /tmp/snapshot/rootfs.$EXT FileSystem || { echo -ne "${Red}ERROR${Reset}: ${Yellow}An error accure while trying to compress the root filesystem.${Reset}"; read nada; exit; }

echo -e "${Yellow}#${Reset} ${Green}Compressing the ISO folder${Reset}"
$COMPRESSION_OPTIONS /tmp/snapshot/isofolder.$EXT ISO || { echo -ne "${Red}ERROR${Reset}: ${Yellow}An error accure while trying to compress the ISO folder.${Reset}"; read nada; exit; }

echo -e "${Yellow}#${Reset} ${Green}Putting it all together${Reset}"
SN="$WORK_DIR/snapshot-`date +%H-%M-%S`.cps"
cd /tmp/snapshot
tar -cf "$SN" * || { echo -ne "${Red}ERROR${Reset}: ${Yellow}An error accure while trying to combine the two compressed archives.${Reset}"; read nada; exit; }
rm -rf /tmp/snapshot

echo -e "${Yellow}#${Reset} ${Green}Snapshot successfuly created${Reset}: ${Yellow}$SN${Reset}"
read nada
exit