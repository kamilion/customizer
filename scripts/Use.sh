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

#################### Some functions used when error accures #####################

iso_mount_error () {
echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to mount. The reason may be that the folder $MOUNT_PATH is currently busy or fail to gain root privilegs${Reset}"
read nada
clean
}

unsquash_error () {
echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to extract the filesystem.squashfs. Make sure you have squashfs-tools installed and build-in kernel module for support of squashfs filesystem and its version is equal or greater than the version used for the compression of the filesystem inside the ISO${Reset}"
read nada
clean
}

clean () {
	echo -e "${Yellow}#${Reset} ${Green}Unmounting ISO${Reset}"
	umount -fl "$MOUNT_PATH" 2> /dev/null
	umount -fl "$ISO" 2> /dev/null
	echo -e "${Yellow}#${Reset} ${Green}Cleaning up temporary directories${Reset}"
	echo -e "   ${Yellow}*${Reset} ${Green}Cleaning up FileSystem${Reset}"
	rm -rf "$WORK_DIR/FileSystem"
	echo -e "   ${Yellow}*${Reset} ${Green}Cleaning up ISO${Reset}"
	rm -rf "$WORK_DIR/ISO"
	exit
}

####################### Checking if the ISO image exists ########################
if [ ! -e "$ISO" ];then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}The ISO image doesn't exists.${Reset}"
	read nada
	exit
fi

################## Cleaning up previous temp folders if exists ##################
if [ -d "$WORK_DIR/FileSystem" ] || [ -d "$WORK_DIR/ISO" ];then
	echo -e "${Yellow}#${Reset} ${Green}Cleaning up temporary directories${Reset}"
	
	echo -e "   ${Yellow}*${Reset} ${Green}Unmounting${Reset}"
	recursive_umount
	umount -fl "$MOUNT_PATH" 2> /dev/null
	
	echo -e "   ${Yellow}*${Reset} ${Green}Cleaning up FileSystem${Reset}"
	rm -rf "$WORK_DIR/FileSystem"
	echo -e "   ${Yellow}*${Reset} ${Green}Cleaning up ISO${Reset}"
	rm -rf "$WORK_DIR/ISO"
	echo -e "   ${Yellow}*${Reset} ${Green}Creating work directories${Reset}"
	mkdir -p "$MOUNT_PATH" "$WORK_DIR/ISO" "$WORK_DIR/FileSystem"
else
	echo -e "${Yellow}#${Reset} ${Green}Creating work directories${Reset}"
	mkdir -p "$MOUNT_PATH" "$WORK_DIR/ISO" "$WORK_DIR/FileSystem"
fi

############################# Mounting the ISO image #############################
echo -e "${Yellow}#${Reset} ${Green}Mounting ISO${Reset}"
mount -t iso9660 -o loop "$ISO" "$MOUNT_PATH" || iso_mount_error

######################## Check if the ISO image is usable ########################
if [ ! -d "$MOUNT_PATH/casper" ] || [ ! -d "$MOUNT_PATH/.disk" ] || [ ! -d "$MOUNT_PATH/isolinux" ] || [ ! -e "$MOUNT_PATH/casper/filesystem.squashfs" ]; then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}This is not a usable ISO image. Make sure you've selected Ubuntu, Xubuntu, Lubuntu, Kubuntu, Ebuntu, Linux Mint or other Ubuntu based ISO image${Reset}"
	read nada
	clean
fi

######################### Extraction filesystem.squashfs ##########################
echo -e "${Yellow}#${Reset} ${Green}Extracting FileSystem${Reset}"
unsquashfs -f -d "$WORK_DIR/FileSystem" "$MOUNT_PATH/casper/filesystem.squashfs" || unsquash_error

################## Check the architecture of the root filesystem ##################
echo -e "${Yellow}#${Reset} ${Green}Checking${Reset}"
ARCH=`chroot "$WORK_DIR/FileSystem" uname -m` || arch_error
if [ "$ARCH" = "x86_64" -o "" ] && [ "`uname -m`" != "x86_64" ]; then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}The selected ISOs filesystem architecture is amd64 and yours is not. You can customize (chroot to install/purge packages, issue some commands etc.)  amd64 architecture ISOs filesystem only if you are running amd64/x86_64 OS release on your machine!'${Reset}"
	read nada
	clean
fi


############ rsync the some files but exclude some that are not needed ############
echo -e "${Yellow}#${Reset} ${Green}Copying ISO files${Reset}"
rsync --exclude=/casper/* --exclude=/md5sum.txt --exclude=/README.diskdefines -a "$MOUNT_PATH/" "$WORK_DIR/ISO" || rsync_error

############################## Unmount the ISO image ##############################
echo -e "${Yellow}#${Reset} ${Green}Unmounting ISO${Reset}"
umount -f "$MOUNT_PATH"
