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

download_new_version () {
echo -e "${Yellow}#${Reset} ${Green}Downloading new version${Reset}: ${Yellow}$VERSION${Reset}"
wget http://sourceforge.net/projects/u-customizer/files/debs/Customizer_${VERSION}_all.deb -O /tmp/Customizer_${VERSION}_all.deb -q -o /tmp/wget.log || wget_error

echo -e "${Yellow}#${Reset} ${Green}Installing new version${Reset}"
dpkg -i /tmp/Customizer_${VERSION}_all.deb

echo -e "${Yellow}#${Reset} ${Green}Installing dependecies${Reset}"
dpkg --configure -a
apt-get install -f

echo -ne "${Yellow}#${Reset} ${Green}DONE${Reset}"
read nada
}



rm -f /tmp/VERSION /tmp/CHANGES /tmp/wget.log
echo -e "${Yellow}#${Reset} ${Green}Downloading version${Reset}"
wget http://sourceforge.net/projects/u-customizer/files/VERSION -O /tmp/VERSION -q -o /tmp/wget.log || wget_error
read VERSION < /tmp/VERSION

if [ "$VERSION" != "3.0.5" ];then
	echo -e "${Yellow}#${Reset} ${Green}Downloading changelog${Reset}"
	wget http://sourceforge.net/projects/u-customizer/files/CHANGES -O /tmp/CHANGES -q -o /tmp/wget.log || wget_error
	echo -e "${Yellow}#${Reset} ${Green}New version is available${Reset}: ${Yellow}v$VERSION${Reset}"
	echo -e "${Yellow}#${Reset} ${Green}With the following changes${Reset}:
	
	${Yellow}`cat /tmp/CHANGES`${Reset}"
	
	while true;do
	echo
	echo -ne "${Green}Do you want to download and install it now?${Reset} ${Yellow}Yes or no${Reset}: "
	read choise
		case $choise in
			y|yes|Yes|YES) download_new_version; break ;;
			n|no|No|NO) break ;;
			*) echo -e "${Red}ERROR${Reset}: ${Yellow}This is not an option${Reset}" ;;
		esac
	done
else
	echo -ne "${Yellow}#${Reset} ${Green}You have the latest version available${Reset}"
	read nada
	exit
fi

