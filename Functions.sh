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
	echo -ne "${Red}ERROR${Reset}: ${Yellow}The filesystem path ($WORK_DIR/FileSystem) isn't usable or has been corruped. Cleaning and start all over again is recommended or use the your latest snapshot (if you've created one).${Reset}"
	read nada
	exit
fi
}

check_sources_list () {
if [ "`cat "$WORK_DIR/FileSystem/etc/apt/sources.list" | grep deb`" = "" ];then
	echo -e "${Red}OVERRIDE${Reset}: ${Yellow}The sources.list has been corrupted or deleted, attempt to be fixed will be made${Reset}"
	id=`grep 'DISTRIB_CODENAME=' "$WORK_DIR/FileSystem/etc/lsb-release" | sed 's/DISTRIB_CODENAME=//'`  
	echo "deb http://archive.ubuntu.com/ubuntu/ $id main" > "$WORK_DIR/FileSystem/etc/apt/sources.list" 
	echo "deb-src http://archive.ubuntu.com/ubuntu/ $id main" >> "$WORK_DIR/FileSystem/etc/apt/sources.list"
fi
}

check_for_X () {
if [ "`pgrep Xorg`" = "" ];then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}X-server (Xorg) is not running.${Reset}"
	read nada
	exit
fi
}

mount_sys () {
echo -e "${Yellow}# ${Green}Mounting${Reset}"
echo -e "   ${Yellow}* ${Green}Mounting${Reset}: ${Yellow}/dev${Reset}" && mount --rbind /dev "$WORK_DIR/FileSystem/dev" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to mount /dev on $WORK_DIR/FileSystem/dev. Maybe it's already mounted and you are trying to double chroot.${Reset}"; read nada; exit; }
echo -e "   ${Yellow}* ${Green}Mounting${Reset}: ${Yellow}/proc${Reset}" && mount --bind /proc "$WORK_DIR/FileSystem/proc" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to mount /proc on $WORK_DIR/FileSystem/proc. Maybe it's already mounted and you are trying to double chroot.${Reset}"; read nada; exit; }
echo -e "   ${Yellow}* ${Green}Mounting${Reset}: ${Yellow}/sys${Reset}" && mount --bind /sys "$WORK_DIR/FileSystem/sys" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to mount /sys on $WORK_DIR/FileSystem/sys. Maybe it's already mounted and you are trying to double chroot.${Reset}"; read nada; exit; }
}

umount_sys () {
echo -e "${Yellow}# ${Green}Unmounting${Reset}"
echo -e "   ${Yellow}* ${Green}Unmounting${Reset}: ${Yellow}/sys${Reset}" 
umount -fl "$WORK_DIR/FileSystem/sys" || { echo -e "${Red}ERROR${Reset}: ${Yellow}Unable to unmount /sys. Try to unmount it manualy or reboot so you don't harm your host OS.${Reset}"; read nada; }
echo -e "   ${Yellow}* ${Green}Unmounting${Reset}: ${Yellow}/proc${Reset}" 
umount -fl "$WORK_DIR/FileSystem/proc" || { echo -e "${Red}ERROR${Reset}: ${Yellow}Unable to unmount /proc. Try to unmount it manualy or reboot so you don't harm your host OS.${Reset}"; read nada; }
echo -e "   ${Yellow}* ${Green}Unmounting${Reset}: ${Yellow}/dev${Reset}" 
umount -fl "$WORK_DIR/FileSystem/dev" || { echo -e "${Red}ERROR${Reset}: ${Yellow}Unable to unmount /dev. Try to unmount it manualy or reboot so you don't harm your host OS.${Reset}"; read nada; }
}

recursive_umount () {
# echo -e "${Yellow}# ${Green}Recursive unmounting${Reset}"
for i in `grep "$WORK_DIR/FileSystem" /proc/mounts | cut -d' ' -f2 | sed 's/\\\040/ /g'`; do
	echo -e "   ${Yellow}* ${Green}Unmounting${Reset}: ${Yellow}`echo $i | sed "s@$WORK_DIR/FileSystem@@g"`${Reset}" 
	umount -fl "$i" || echo -e "${Red}ERROR${Reset}: ${Yellow}Unable to unmount $i. Try to unmount it manualy or reboot so you don't harm your host OS.${Reset}"
done
}

mount_dbus () {
mkdir -p "$WORK_DIR/FileSystem/var/lib/dbus"
mkdir -p "$WORK_DIR/FileSystem/var/run/dbus"

echo -e "   ${Yellow}* ${Green}Mounting${Reset}: ${Yellow}/var/lib/dbus${Reset}" && mount --bind /var/lib/dbus "$WORK_DIR/FileSystem/var/lib/dbus" || echo -e "${Red}ERROR${Reset}: ${Yellow}Unable to mount /var/run/dbus.${Reset}"
echo -e "   ${Yellow}* ${Green}Mounting${Reset}: ${Yellow}/var/run/dbus${Reset}" && mount --bind /var/run/dbus "$WORK_DIR/FileSystem/var/run/dbus" || echo -e "${Red}ERROR${Reset}: ${Yellow}Unable to mount /var/run/dbus.${Reset}"
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
