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

source /opt/Customizer/settings.conf
Reset='\e[0m'
Red='\e[1;31m'
Green='\e[1;32m'
Yellow='\e[1;33m'

############# Common functions #############
check_fs_dir () {
if [ ! -d "$WORK_DIR/FileSystem" ];then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}The filesystem path ($WORK_DIR/FileSystem) doesn't exists. Have you disassambled ISO image at all?${Reset}"
	read nada
	exit
fi

if [ ! -d "$WORK_DIR/FileSystem/etc" ] || [ ! -d "$WORK_DIR/FileSystem/usr" ] || [ ! -d "$WORK_DIR/FileSystem/root" ];then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}The filesystem path ($WORK_DIR/FileSystem) isn't usable or has been corruped.Cleaning and start all over again is recommended or use the your latest snapshot (if you've created one).${Reset}"
	read nada
	exit
fi
}

check_sources_list () {
if [ "`cat "$WORK_DIR/FileSystem/etc/apt/sources.list" | grep deb`" = "" ];then
	echo -e "${Red}OVERRIDE${Reset}: ${Yellow}The sources.list has been corrupted or deleted, attempt to be fixed will be made${Reset}"
	id=`cat $WORK_DIR/FileSystem/etc/lsb-release | grep DISTRIB_CODENAME=* | sed 's/DISTRIB_CODENAME=//'`  
	echo "deb http://archive.ubuntu.com/ubuntu/ $id main" > "$WORK_DIR/FileSystem/etc/apt/sources.list" 
	echo "deb-src http://archive.ubuntu.com/ubuntu/ $id main" >> "$WORK_DIR/FileSystem/etc/apt/sources.list"
fi
}


mount_sys () {
echo -e "${Yellow}# ${Green}Mounting${Reset}"
mount --rbind /dev "$WORK_DIR/FileSystem/dev" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to mount /dev on $WORK_DIR/FileSystem/dev. Maybe it's already mounted and you are trying to double chroot.${Reset}"; read nada; exit; }
mount --bind /proc "$WORK_DIR/FileSystem/proc" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to mount /proc on $WORK_DIR/FileSystem/proc. Maybe it's already mounted and you are trying to double chroot.${Reset}"; read nada; exit; }
mount --bind /sys "$WORK_DIR/FileSystem/sys" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to mount /sys on $WORK_DIR/FileSystem/sys. Maybe it's already mounted and you are trying to double chroot.${Reset}"; read nada; exit; }
}

umount_sys () {
echo -e "${Yellow}# ${Green}Unmounting${Reset}"
for i in `df -a -l | grep "$WORK_DIR/FileSystem" | awk '{print $6}'`;do
	umount -fl "$i" || echo -e "${Red}ERROR${Reset}: ${Yellow}Unable to unmount $i. Try to unmount it manualy or reboot so you don't harm your host OS.${Reset}"
done
}

############# Errors #############

rsync_error () {
echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to copy files! Make sure you have rsync installed${Reset}"
read nada
clean
}
	
chroot_hook_error () {
echo -ne "${Red}ERROR${Reset}: ${Yellow}The chroot hook has returned exit status by internal command${Reset}"
read nada
}

wget_error () {
	echo -ne "${Red}ERROR${Reset}: ${Yellow}Wget was unable to download the requsted file${Reset}"
	echo
	cat /tmp/wget.log
	echo
}

arch_error () {
	echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to get the architecture of the distribution${Reset}"
	read nada
	exit
}

dist_error () {
	echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to get the distribution${Reset}"
	read nada
	exit
}

version_error () {
	echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to get the version of the distribution${Reset}"
	read nada
	exit
}