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

#################### check configs & dirs before going further ####################
echo -e "${Yellow}# ${Green}Checking${Reset}"
check_fs_dir
check_sources_list

if [ ! -d "$WORK_DIR/ISO/isolinux" ]; then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}$WORK_DIR/ISO/isolinux doesnt exist. Please, clean and select ISO again to repeat the extraction proccess or use the syslinux package to restore it.${Reset}"
	read nada
	exit
fi

if [ ! -d "$WORK_DIR/ISO/.disk" ]; then
	echo -e "${Red}OVERRIDE${Reset}: ${Yellow}Creating${Reset}: ${Green}$WORK_DIR/ISO/.disk/cd_type${Reset}"
	mkdir -p "$WORK_DIR/ISO/.disk"
fi

if [ ! -d "$WORK_DIR/ISO/casper" ]; then
	echo -e "${Red}OVERRIDE${Reset}: ${Yellow}Creating${Reset}: ${Green}$WORK_DIR/ISO/.disk/cd_type${Reset}"
	mkdir -p "$WORK_DIR/ISO/casper"
fi

if [ ! -e "$WORK_DIR/ISO/.disk/cd_type" ]; then
	echo -e "${Red}OVERRIDE${Reset}: ${Yellow}Creating${Reset}: ${Green}$WORK_DIR/ISO/.disk/cd_type${Reset}"
	echo "full_cd/single" > "$WORK_DIR/ISO/.disk/cd_type"
fi

if [ -e "$WORK_DIR/usr/bin/ubiquity" ] && [ ! -e "$WORK_DIR/ISO/.disk/base_installable" ]; then
	echo -e "${Red}OVERRIDE${Reset}: ${Yellow}Creating${Reset}: ${Green}$WORK_DIR/ISO/.disk/base_installable${Reset}"
	echo > "$WORK_DIR/ISO/.disk/base_installable"
else
	rm -f "$WORK_DIR/ISO/.disk/base_installable"
fi

if [ ! -e "$WORK_DIR/ISO/.disk/casper-uuid-generic" ]; then
	echo -e "${Red}OVERRIDE${Reset}: ${Yellow}Creating${Reset}: ${Green}$WORK_DIR/ISO/.disk/casper-uuid-generic${Reset}"
	echo "f01d0b93-4f0e-4e95-93ae-e3d0e114d4f7" > "$WORK_DIR/ISO/.disk/casper-uuid-generic"
fi

if [ ! -e "$WORK_DIR/ISO/.disk/release_notes_url" ]; then
	echo -e "${Red}OVERRIDE${Reset}: ${Yellow}Creating${Reset}: ${Green}$WORK_DIR/ISO/.disk/release_notes_url${Reset}"
	echo "http://www.ubuntu.com/getubuntu/releasenotes" > "$WORK_DIR/ISO/.disk/release_notes_url"
fi

if [ ! -e "$WORK_DIR/FileSystem/etc/lsb-release" ]; then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}$WORK_DIR/FileSystem/etc/lsb-release dosn't exists. Create it manualy or clean and start all-over again.${Reset}"
	read nada
	exit
fi

if [ ! -e "$WORK_DIR/FileSystem/etc/casper.conf" ]; then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}$WORK_DIR/FileSystem/etc/casper.conf dosn't exists. Create it manualy or clean and start all-over again.${Reset}"
	read nada
	exit
fi

#################### setting up the root filesystem #####################

echo -e "${Yellow}# ${Green}Loading configs${Reset}"
ARCH=`chroot "$WORK_DIR/FileSystem" uname -m` || arch_error
RELEASE_NOTES_URL="`cat "$WORK_DIR/ISO/.disk/release_notes_url"`"
DIST=`grep DISTRIB_ID= "$WORK_DIR/FileSystem/etc/lsb-release" | sed 's/DISTRIB_ID=//'`
VERSION=`grep DISTRIB_RELEASE= "$WORK_DIR/FileSystem/etc/lsb-release" | sed 's/DISTRIB_RELEASE=//'`
CODENAME=`grep DISTRIB_CODENAME= "$WORK_DIR/FileSystem/etc/lsb-release" | sed 's/DISTRIB_CODENAME=//'`
LIVEUSERNAME=`grep "export USERNAME=" "$WORK_DIR/FileSystem/etc/casper.conf" | sed 's/export USERNAME=//;s/\"//g'`

to_clean="$WORK_DIR/$DIST-$ARCH-$VERSION.iso $WORK_DIR/ISO/casper/filesystem.squashfs $WORK_DIR/ISO/casper/initrd.lz $WORK_DIR/ISO/casper/vmlinuz $WORK_DIR/ISO/casper/filesystem.manifest $WORK_DIR/ISO/casper/filesystem.manifest-desktop $WORK_DIR/ISO/casper/filesystem.size $WORK_DIR/ISO/casper/README.diskdefines $WORK_DIR/ISO/md5sum.txt"
echo -e "${Yellow}# ${Green}Cleaning up from previous build${Reset}"
for i in $to_clean;do
	if [ -e "$i" ];then
		echo -e "   ${Yellow}* ${Green}Deleting${Reset}: ${Yellow}$i${Reset}"
		rm -f "$i"
	fi
done

echo -e "${Yellow}# ${Green}Setting up Distribution information${Reset}"
echo -e "   ${Yellow}*${Reset} ${Green}Rebranding motd${Reset}"
echo -e "$DIST $VERSION \n\n Welcome to $DIST! \n * $RELEASE_NOTES_URL\n\n" > "$WORK_DIR/FileSystem/etc/motd"
cat > "$WORK_DIR/FileSystem/etc/update-motd.d/10-help-text" << EOF
#!/bin/sh
if uname -r | grep -qs "\-server"; then
	echo
	echo "Welcome to $DIST Server!"
	echo " * $RELEASE_NOTES_URL"
	echo
	echo
else
	echo
	echo "Welcome to $DIST!"
	echo " * $RELEASE_NOTES_URL"
	echo
	echo
fi
EOF

echo -e "${Yellow}# ${Green}Doing some preparations${Reset}"
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

echo -e "${Yellow}   *${Reset} ${Green}Updating packages database${Reset}"
apt-get update -qq
echo -e "${Yellow}   *${Reset} ${Green}Making sure everything is configured${Reset}"
dpkg --configure -a
apt-get install -f -y -qq

if [ ! -f /initrd.img ] || [ ! -f /vmlinuz ]; then
	echo -e "${Yellow}   *${Reset} ${Green}Purging Kernels (if any)${Reset}"
	apt-get purge --yes linux-image* linux-headers* -qq
	echo -e "${Yellow}   *${Reset} ${Green}Installing Kernel${Reset}"
	apt-get install --yes linux-image-generic linux-headers-generic -qq
else
	echo -e "${Yellow}   *${Reset} ${Green}Installing the latest initramfs-tools${Reset}"
	apt-get install --yes initramfs-tools -qq
	echo -e "${Yellow}   *${Reset} ${Green}Updating/creating Kernel image${Reset}"
	update-initramfs -u
fi

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
echo -e "${Yellow}# ${Green}Entering Chroot env.${Reset}"
chroot "$WORK_DIR/FileSystem" bash /tmp/script.sh || chroot_hook_error
umount_sys
recursive_umount

echo -e "${Yellow}# ${Green}Copying boot files${Reset}"
cp -f "$WORK_DIR/FileSystem/initrd.img" "$WORK_DIR/ISO/casper/initrd.lz" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to copy the initrd.img file.${Reset}"; read nada; exit; }

cp -f "$WORK_DIR/FileSystem/vmlinuz" "$WORK_DIR/ISO/casper/vmlinuz" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to copy the vmlinuz file.${Reset}"; read nada; exit; }

if [ "$BOOT_FILES" = "1" ]; then
	echo -e "${Yellow}# ${Green}Deleteing boot files${Reset}"
	rm -f "$WORK_DIR/FileSystem/boot/*-generic"
fi

#################### creting ISO image #####################

echo -e "${Yellow}# ${Green}Creating squashed FileSystem${Reset}"
mksquashfs "$WORK_DIR/FileSystem" "$WORK_DIR/ISO/casper/filesystem.squashfs" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to squash the filesystem.${Reset}"; read nada; exit; }

if (( "`du -sx "$WORK_DIR/ISO/casper/filesystem.squashfs" | cut -f1`" > "4000000" ));then
	echo -ne "${Red}ERROR${Reset}: ${Yellow}The squashed filesystem size is greater than 4GB. Reduce its size by removing packages, locales and/or other none-essentials and retry the build process.${Reset}"
	read nada
	exit
fi

echo "`du -sx --block-size=1 $WORK_DIR/FileSystem | cut -f1`" > "$WORK_DIR/ISO/casper/filesystem.size" || { echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to calculate the size of the filesystem.${Reset}"; read nada; exit; }

echo -e "${Yellow}#${Reset} ${Green}Creating Manifest files${Reset}"
echo -e "   ${Yellow}*${Reset} ${Green}Creating filesystem.manifest${Reset}"
chroot "$WORK_DIR/FileSystem" dpkg-query -W --showformat='${Package} ${Version}\n' > "$WORK_DIR/ISO/casper/filesystem.manifest" || { zenity --error --text="Unable to chroot into the filesystem to create packages list (manifest file). Are you trying to customize 64-bit (x86_64/amd64) ISO from 32-bit (x86/i386) host OS? If so read the FAQ on the forum: http://sourceforge.net/apps/phpbb/u-customizer/viewtopic.php?f=1&t=3"; exit; }
echo -e "   ${Yellow}*${Reset} ${Green}Creating filesystem.manifest-desktop${Reset}"
cp -f "$WORK_DIR/ISO/casper/filesystem.manifest" "$WORK_DIR/ISO/casper/filesystem.manifest-desktop"
REMOVE='ubiquity casper live-initramfs user-setup discover1 xresprobe os-prober libdebian-installer4'
for i in $REMOVE 
do
        sed -i "/${i}/d" "$WORK_DIR/ISO/casper/filesystem.manifest-desktop"
done

echo -e "${Yellow}# ${Green}Rebranding ISO files${Reset}"
echo -e "   ${Yellow}*${Reset} ${Green}Creating README.diskdefines${Reset}"
cat > "$WORK_DIR/ISO/README.diskdefines" << EOF
#define DISKNAME  $DIST $VERSION "$CODENAME" - Release $ARCH
#define TYPE  binary
#define TYPEbinary  1
#define ARCH  $ARCH
#define ARCH$ARCH  1
#define DISKNUM  1
#define DISKNUM1  1
#define TOTALNUM  0
#define TOTALNUM0  1
EOF

echo -e "   ${Yellow}*${Reset} ${Green}Creating disk info${Reset}"
echo "$DIST $VERSION "$CODENAME" - Release $ARCH (`date "+%Y%m%d"`)" > "$WORK_DIR/ISO/.disk/info"

cd "$WORK_DIR/ISO"
if [ "$WIN_EXECUTABLES" = "1" ]; then
	echo -e "${Yellow}# ${Green}Deleteing Windows executable files${Reset}"
	rm -rf "$WORK_DIR/ISO/bin"
	rm -rf "$WORK_DIR/ISO/disctree"
	rm -rf "$WORK_DIR/ISO/pics"
	rm -rf "$WORK_DIR/ISO/programs"
	rm -f "$WORK_DIR/ISO/autorun.inf"
	rm -f "$WORK_DIR/ISO/start.bmp"
	rm -f "$WORK_DIR/ISO/start.exe"
	rm -f "$WORK_DIR/ISO/start.ini"
	rm -f "$WORK_DIR/ISO/ubuntu.ico"
	rm -f "$WORK_DIR/ISO/kubuntu.ico"
	rm -f "$WORK_DIR/ISO/xubuntu.ico"
	rm -f "$WORK_DIR/ISO/lubuntu.ico"
	rm -f "$WORK_DIR/ISO/wubi-cdboot.exe"
	rm -f "$WORK_DIR/ISO/wubi.exe"
	rm -f "$WORK_DIR/ISO/umenu.exe"
	rm -f "$WORK_DIR/ISO/usb-creator.exe"
fi

################# Creating md5sum and ISO  #################

echo -e "${Yellow}# ${Green}Creating MD5Sums${Reset}"
(find . -type f -print0 | xargs -0 md5sum | grep -v "\./md5sum.txt") > md5sum.txt || { echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to create the md5sum.${Reset}"; read nada; exit; }

echo -e "${Yellow}# ${Green}Creating ISO${Reset}"
(genisoimage -r -V "$DIST-$ARCH-$VERSION" -b isolinux/isolinux.bin -c isolinux/boot.cat -cache-inodes -J -l -no-emul-boot -boot-load-size 4 -boot-info-table -o "$WORK_DIR/$DIST-$ARCH-$VERSION.iso" -input-charset utf-8 .
chmod 555 $WORK_DIR/$DIST-$ARCH-$VERSION.iso
echo -e "${Yellow}# ${Green}Successfuly created ISO image${Reset}: ${Yellow}$WORK_DIR/$DIST-$ARCH-$VERSION.iso${Reset}"
read nada) || { echo -ne "${Red}ERROR${Reset}: ${Yellow}Unable to create ISO image.${Reset}"; read nada; exit; }
