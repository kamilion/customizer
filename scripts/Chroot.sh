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

echo -e "${Yellow}#${Reset} ${Green}Checking${Reset}"
check_fs_dir
check_sources_list

echo -e "${Yellow}#${Reset} ${Green}Doing some preparations${Reset}"
cp -f /etc/hosts "$WORK_DIR/FileSystem/etc"
cp -f /etc/resolv.conf "$WORK_DIR/FileSystem/etc"
echo chroot > "$WORK_DIR/FileSystem/etc/debian_chroot"

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

/bin/bash

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
umount_sys
recursive_umount
