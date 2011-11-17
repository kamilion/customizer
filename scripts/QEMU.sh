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
check_for_X

echo -e "${Yellow}#${Reset} ${Green}Getting the configs${Reset}"
ARCH=`chroot "$WORK_DIR/FileSystem" dpkg --print-architecture` || arch_error
DIST=`grep DISTRIB_ID= "$WORK_DIR/FileSystem/etc/lsb-release" | sed 's/DISTRIB_ID=//'` || dist_error
VERSION=`grep DISTRIB_RELEASE= "$WORK_DIR/FileSystem/etc/lsb-release" | sed 's/DISTRIB_RELEASE=//'` || version_error

echo -e "${Yellow}#${Reset} ${Green}Checking${Reset}"
if [ ! -e "$WORK_DIR/$DIST-$ARCH-$VERSION.iso" ];then
	echo -e "${Red}ERROR${Reset}: ${Yellow}ISO Image doesn't exists${Reset}: ${Green}$WORK_DIR/$DIST-$ARCH-$VERSION.iso${Reset}"
	if [ "`ls "$WORK_DIR/*.iso" 2> /dev/null`" != "" ];then
		echo -e "${Red}OVERRIDE${Reset}: ${Yellow}Choose one of the following ISO images${Reset}:"
		
		while true;do
		echo
		ls -1 "$WORK_DIR/*.iso" | sed "s/$WORK_DIR//;s/\.iso//"
	
		echo
		echo -ne "${Yellow}What shall it be?${Reset}: "
		read choise
	
		if [ ! -e "$WORK_DIR/$choise.iso" ];then
			echo -e "${Red}ERROR${Reset}: ${Yellow}This is not an option.${Reset}"	
		else
			echo -e "${Yellow}#${Reset} ${Green}Running QEMU with ISO Image${Reset}: ${Yellow}$WORK_DIR/$choise.iso${Reset}"
			qemu -cdrom "$WORK_DIR/$choise.iso" -m $VRAM
		fi
		done
	fi
else
	echo -e "${Yellow}#${Reset} ${Green}Running QEMU with ISO Image${Reset}: ${Yellow}$WORK_DIR/$DIST-$ARCH-$VERSION.iso${Reset}"
	qemu -cdrom "$WORK_DIR/$DIST-$ARCH-$VERSION.iso" -m $VRAM	
fi

