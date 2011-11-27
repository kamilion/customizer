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
check_lock
check_sources_list

if [ ! -e "$DEB" ];then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}DEB package doesn't exists.${Reset}"
	read nada
	exit
fi

case "$DEB" in
	*.deb) true ;;
	*) echo -ne "${Red}ERROR${Reset}: ${Yellow}This is not DEB package.${Reset}"; read nada; exit ;;
esac


echo -e "${Yellow}#${Reset} ${Green}Doing some preparations${Reset}"
cp -f /etc/hosts "$WORK_DIR/FileSystem/etc"
cp -f /etc/resolv.conf "$WORK_DIR/FileSystem/etc"
mv "$WORK_DIR/FileSystem/sbin/initctl" "$WORK_DIR/FileSystem/sbin/initctl.blocked"
ln -s "$WORK_DIR/FileSystem/bin/true" "$WORK_DIR/FileSystem/sbin/initctl"
mv "$WORK_DIR/FileSystem/usr/sbin/update-grub" "$WORK_DIR/FileSystem/usr/sbin/update-grub.blocked"
ln -s "$WORK_DIR/FileSystem/bin/true" "$WORK_DIR/FileSystem/usr/sbin/update-grub"
echo chroot > "$WORK_DIR/FileSystem/etc/debian_chroot"
rm -f "$WORK_DIR/FileSystem/tmp/*deb"
cp "$DEB" "$WORK_DIR/FileSystem/tmp"
touch "$WORK_DIR/FileSystem/tmp/lock_chroot"

cat > "$WORK_DIR/FileSystem/tmp/script.sh" << EOF
Reset='\e[0m'
Red='\e[1;31m'
Green='\e[1;32m'
Yellow='\e[1;33m'

echo -e "${Yellow}   *${Reset} ${Green}Setting up${Reset}"
export HOME=/root
export LC_ALL=C
dpkg-divert --local --rename --add /sbin/initctl
ln -f -s /bin/true /sbin/initctl

echo -e "${Yellow}   *${Reset} ${Green}Making sure everything is configured${Reset}"
dpkg --configure -a
apt-get install -f -y -q
echo -e "${Yellow}   *${Reset} ${Green}Updating packages database${Reset}"
apt-get update -qq


echo -e "${Yellow}   *${Reset} ${Green}Installing the DEB Package${Reset}"
dpkg -i /tmp/*.deb
echo -e "${Yellow}   *${Reset} ${Green}Installing its dependecies${Reset}"
apt-get install -f -y -q

echo -e "${Yellow}   *${Reset} ${Green}Cleaning up${Reset}"
apt-get clean
dpkg-divert --remove /sbin/initctl
rm -f /etc/debian_chroot
rm -f /etc/hosts
rm -f /etc/resolv.conf
rm -f /sbin/initctl
rm -f ~/.bash_history
rm -f /boot/*.bak
rm -f /var/lib/dpkg/*-old
rm -f /var/lib/aptitude/*.old
rm -f /var/cache/debconf/*.dat-old
rm -f /var/log/*.gz
rm -rf /tmp/*
EOF

mount_sys
echo -e "${Yellow}#${Reset} ${Green}Entering Chroot env.${Reset}"
chroot "$WORK_DIR/FileSystem" bash /tmp/script.sh || chroot_hook_error
rm "$WORK_DIR/FileSystem/sbin/initctl"
mv "$WORK_DIR/FileSystem/sbin/initctl.blocked" "$WORK_DIR/FileSystem/sbin/initctl"
rm "$WORK_DIR/FileSystem/usr/sbin/update-grub"
mv "$WORK_DIR/FileSystem/usr/sbin/update-grub.blocked" "$WORK_DIR/FileSystem/usr/sbin/update-grub"
rm -f "$WORK_DIR/tmp/lock_chroot"
umount_sys
recursive_umount