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

echo -e "${Yellow}#${Reset} ${Green}Checking${Reset}"
check_fs_dir
check_lock
check_sources_list

if [ "`pgrep Xorg`" = "" ];then
	PACKAGE_MANAGERS="aptitude aptsh"
else
	PACKAGE_MANAGERS="software-center synaptic aptitude aptsh"
fi

PACKAGE_MANAGER=""
if [ ! -e "$WORK_DIR/FileSystem/usr/bin/software-center" ] && [ ! -e "$WORK_DIR/FileSystem/usr/sbin/synaptic" ] && [ ! -e "$WORK_DIR/FileSystem/usr/bin/aptitude" ] && [ ! -e "$WORK_DIR/FileSystem/usr/bin/aptsh" ];then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}No supported package manager were detected${Reset}"
	read nada
	exit
fi

while true;do
echo
	
for i in $PACKAGE_MANAGERS; do
if [ -e "$WORK_DIR/FileSystem/usr/sbin/$i" ] || [ -e "$WORK_DIR/FileSystem/usr/bin/$i" ];then
	echo $i
fi
done
	
echo
echo -ne "${Yellow}What shall it be?${Reset}: "
read choise

if [ ! -e "$WORK_DIR/FileSystem/usr/sbin/$choise" ] && [ ! -e "$WORK_DIR/FileSystem/usr/bin/$choise" ];then
	echo -e "${Red}ERROR${Reset}: ${Yellow}This is not an option.${Reset}"	
else
	export PACKAGE_MANAGER=$choise
	break
fi
done

echo -e "${Yellow}#${Reset} ${Green}Doing some preparations${Reset}"
cp -f /etc/hosts "$WORK_DIR/FileSystem/etc"
cp -f /etc/resolv.conf "$WORK_DIR/FileSystem/etc"
mv "$WORK_DIR/FileSystem/sbin/initctl" "$WORK_DIR/FileSystem/sbin/initctl.blocked"
ln -s "$WORK_DIR/FileSystem/bin/true" "$WORK_DIR/FileSystem/sbin/initctl"
mv "$WORK_DIR/FileSystem/usr/sbin/update-grub" "$WORK_DIR/FileSystem/usr/sbin/update-grub.blocked"
ln -s "$WORK_DIR/FileSystem/bin/true" "$WORK_DIR/FileSystem/usr/sbin/update-grub"
echo chroot > "$WORK_DIR/FileSystem/etc/debian_chroot"
touch "$WORK_DIR/FileSystem/tmp/lock_chroot"

# Create script to setup chroot env.
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
echo -e "${Yellow}   *${Reset} ${Green}Installing the latest Dbus${Reset}"
apt-get install --yes dbus -qq

echo -e "${Yellow}   *${Reset} ${Green}Running package manager:${Reset} ${Yellow}$PACKAGE_MANAGER${Reset}"
`which $PACKAGE_MANAGER`

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
