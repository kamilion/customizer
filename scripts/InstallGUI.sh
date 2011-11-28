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

while true;do
	echo -ne "${Red}NOTE${Reset}: ${Yellow}ONLY CORE PACKAGES WILL BE ISNTALLED!${Reset}"
	echo "
	
	1. Gnome
	2. KDE
	3. XFCE4
	4. LXDE
	5. Openbox
	6. Fluxbox
	7. Blackbox
	8. IceWM"
	echo
	echo -ne "${Yellow}Which GUI (Desktop Environment/Window Manager) do you want to install?${Reset}: "
	
	read choise
		case $choise in
			1) export GUI_PACKAGES="xserver-xorg xinit gnome-session gnome-panel gdm gnome-terminal"; break ;;
			2) export GUI_PACKAGES="xserver-xorg xinit kde-standard"; break ;;
			3) export GUI_PACKAGES="xserver-xorg xinit xfce4 # xfce4-session xfce4-panel xfce4-terminal"; break ;;
			4) export GUI_PACKAGES="xserver-xorg xinit lxde-core lxterminal lxdm"; break ;;
			5) export GUI_PACKAGES="xserver-xorg xinit xterm openbox menu slim"; break ;;
			6) export GUI_PACKAGES="xserver-xorg xinit xterm fluxbox menu slim"; break ;;
			7) export GUI_PACKAGES="xserver-xorg xinit xterm blackbox menu slim"; break ;;
			8) export GUI_PACKAGES="xserver-xorg xinit icewm-lite menu xdm"; break ;;
			*) echo -e "${Red}ERROR${Reset}: ${Yellow}This is not an option${Reset}" ;;
		esac
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

cat > "$WORK_DIR/FileSystem/tmp/script.sh" << EOF
Reset='\e[0m'
Red='\e[1;31m'
Green='\e[1;32m'
Yellow='\e[1;33m'

echo -e "${Yellow}   *${Reset} ${Green}Setting up${Reset}"
export HOME=/root
export LC_ALL=C

echo -e "${Yellow}   *${Reset} ${Green}Making sure everything is configured${Reset}"
dpkg --configure -a
apt-get install -f -y -q
echo -e "${Yellow}   *${Reset} ${Green}Updating packages database${Reset}"
apt-get update -qq

echo -e "${Yellow}   *${Reset} ${Green}Installing GUI${Reset}"
apt-get install -y $GUI_PACKAGES --no-install-recommends

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