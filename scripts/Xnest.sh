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

xephyr_error () {
echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to execute Xephyr, is it installed?${Reset}"
read nada
exit
}

echo -e "${Yellow}#${Reset} ${Green}Checking${Reset}"
check_for_X
check_fs_dir
check_lock
check_sources_list

AVAILABLE=`(ls "$WORK_DIR/FileSystem/usr/share/xsessions" | wc -l) 2> /dev/null`
case $AVAILABLE in
	0) echo -ne "${Red}ERROR${Reset}: ${Yellow}There are not X-session available, chroot and install Desktop Environment/Window Manager${Reset}"; read nada; exit ;;
	1) XSESSION="`ls -F "$WORK_DIR/FileSystem/usr/share/xsessions" | sed 's/\.desktop//'`"
	   echo -e "${Red}OVERRIDE${Reset}: ${Yellow}There is only one X-session available:${Reset} ${Green}$XSESSION${Reset}"
	   export XSESSION=$XSESSION ;;
	*) echo -e "${Red}OVERRIDE${Reset}: ${Yellow}Multiple X-sessions available, choose which one to execute:${Reset}"
	
	while true;do
	echo
	for i in `ls "$WORK_DIR/FileSystem/usr/share/xsessions" | sed 's/.desktop//'`;do
		echo -e "${Green}$i${Reset}"
	done
	
	echo
	echo -ne "${Yellow}What shall it be?${Reset}: "
	read choise
	
	if [ ! -e "$WORK_DIR/FileSystem/usr/share/xsessions/$choise.desktop" ];then
		echo -e "${Red}ERROR${Reset}: ${Yellow}This is not an option.${Reset}"	
	else
		export XSESSION=$choise
		break
	fi
	done ;;
esac

echo -e "${Yellow}#${Reset} ${Green}Doing some preparations${Reset}"
cp -f /etc/hosts "$WORK_DIR/FileSystem/etc"
cp -f /etc/resolv.conf "$WORK_DIR/FileSystem/etc"
mv "$WORK_DIR/FileSystem/sbin/initctl" "$WORK_DIR/FileSystem/sbin/initctl.blocked"
ln -s "$WORK_DIR/FileSystem/bin/true" "$WORK_DIR/FileSystem/sbin/initctl"
mv "$WORK_DIR/FileSystem/usr/sbin/update-grub" "$WORK_DIR/FileSystem/usr/sbin/update-grub.blocked"
ln -s "$WORK_DIR/FileSystem/bin/true" "$WORK_DIR/FileSystem/usr/sbin/update-grub"
echo chroot > "$WORK_DIR/FileSystem/etc/debian_chroot"
touch "$WORK_DIR/FileSystem/tmp/lock_chroot"

cat > "$WORK_DIR/FileSystem/tmp/script.sh" << "EOF"
Reset='\e[0m'
Red='\e[1;31m'
Green='\e[1;32m'
Yellow='\e[1;33m'

echo -e "${Yellow}   *${Reset} ${Green}Setting up${Reset}"
export DISPLAY=localhost:9
export HOME=/root
export LC_ALL=C
dbus-uuidgen --ensure

echo -e "${Yellow}   *${Reset} ${Green}Making sure everything is configured${Reset}"
dpkg --configure -a
apt-get install -f -y -q
echo -e "${Yellow}   *${Reset} ${Green}Updating packages database${Reset}"
apt-get update -qq
echo -e "${Yellow}   *${Reset} ${Green}Installing the latest Dbus${Reset}"
apt-get install --yes dbus -qq

echo -e "${Yellow}   *${Reset} ${Green}Executing X-Session:${Reset} ${Yellow}$XSESSION${Reset}"
`grep -m 1 "Exec=" /usr/share/xsessions/$XSESSION.desktop | sed 's/Exec=//'`

echo -e "${Yellow}   *${Reset} ${Green}Cleaning up${Reset}"
apt-get clean
dpkg-divert --remove /sbin/initctl
rm -f /etc/debian_chroot
rm -f /etc/hosts
rm -f /etc/resolv.conf
rm -f ~/.bash_history
rm -f /boot/*.bak
rm -f /var/lib/dpkg/*-old
rm -f /var/lib/aptitude/*.old
rm -f /var/cache/debconf/*.dat-old
rm -f /var/log/*.gz
rm -rf /tmp/*
EOF

# Start Xephyr and the script
# FIXME: error not shown when unable to execute Xephyr
# (Xephyr -ac -screen $RESOLUTION -br :9 &) || xephyr_error
echo -e "${Yellow}#${Reset} ${Green}Starting Xephyr${Reset}"
Xephyr -ac -screen $RESOLUTION -br :9 &

xhost +local:
mount_sys
mount_dbus
echo -e "${Yellow}#${Reset} ${Green}Entering Chroot env.${Reset}"
chroot "$WORK_DIR/FileSystem" bash /tmp/script.sh || chroot_hook_error
rm "$WORK_DIR/FileSystem/sbin/initctl"
mv "$WORK_DIR/FileSystem/sbin/initctl.blocked" "$WORK_DIR/FileSystem/sbin/initctl"
rm "$WORK_DIR/FileSystem/usr/sbin/update-grub"
mv "$WORK_DIR/FileSystem/usr/sbin/update-grub.blocked" "$WORK_DIR/FileSystem/usr/sbin/update-grub"
rm -f "$WORK_DIR/tmp/lock_chroot"
umount_sys
recursive_umount
xhost -local:

echo -e "${Yellow}#${Reset} ${Green}Stoping Xephyr${Reset}"
killall Xephyr

echo -e "${Yellow}#${Reset} ${Green}Remove some unwanted files/dirs${Reset}"
rm -rf "$WORK_DIR/FileSystem/root/.kde/share/apps/nepomuk"
rm -rf "$WORK_DIR/FileSystem/root/.cache"
rm -rf "$WORK_DIR/FileSystem/root/.dbus"
rm -rf "$WORK_DIR/FileSystem/root/.thumbnails"

echo -e "${Yellow}#${Reset} ${Green}Copying the changes to skel${Reset}"
cp -ru "$WORK_DIR/FileSystem/root/"* "$WORK_DIR/FileSystem/etc/skel" 2> /dev/null
cp -ru "$WORK_DIR/FileSystem/root/".??* "$WORK_DIR/FileSystem/etc/skel" 2> /dev/null
