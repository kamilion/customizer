#!/usr/bin/env bash
# Customizer - Advanced LiveCD Remastering Tool
# Copyright (C) 2011  Ivailo Monev
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Homepage: https://github.com/fluxer/Customizer
# Wiki: https://github.com/fluxer/Customizer/wiki
# Issues: https://github.com/fluxer/Customizer/issues
#
set -e
source /opt/Customizer/common
source /opt/Customizer/settings.conf

Root_it() {
	if [ "$UID" != "0" ];then
		WARNING_MESSAGE "You are not root! Promting for password"
		su -c "$1"
    else
        "$1"
	fi
}

Usage () {
echo "
 Main options:

     -u|--use       Exctract ISO image
     -c|--chroot    Chroot into the filesystem
     -x|--xnest     Execute nested X-session
     -e|--sources   Edit sources.list
     -p|--pkgm      Execute package manager
     -d|--deb       Install Debian package
     -k|--hook      Execute hook
     -g|--gui       Install GUI (DE/WM)
     -s|--snapshot  Creates snapshot of your current work
     -i|--import    Imports created snapshot
     -r|--rebuild   Rebuild the ISO image
     -q|--qemu      Test the builded image with QEMU
     -t|--clean     Clean all temporary files and folders

 Other options:
     
     -h|--help      Display this message
     -v|--version   Show the current version and more
"
}

Version () {
echo "
Customizer v3.1.0

Links:

  Homepage: https://github.com/fluxer/Customizer
  Wiki: https://github.com/fluxer/Customizer/wiki
  Issues: https://github.com/fluxer/Customizer/issues


Credits:

  Main developer:
    Ivailo Monev (a.k.a SmiL3y)
    <xakepa10@gmail.com>

  PPA maintainer:
    Michał Głowienka (a.k.a. eloaders)
    <eloaders@yahoo.com>

  Documentation:
    Mubiin Kimura (a.k.a. clearkimura)
    <clearkimura@gmail.com>
"
}

if [ "$#" != "0" ];then
	for arg in "$@"; do
		case $arg in
			-u|--use) Root_it/opt/Customizer/scripts/extract ;;
			-c|--chroot) Root_it /opt/Customizer/scripts/chroot ;;
			-x|--xnest) Root_it /opt/Customizer/scripts/xnest ;;
			-e|--sources) Root_it /opt/Customizer/scripts/edit_sources ;;
			-p|--pkgm) Root_it /opt/Customizer/scripts/package_manager ;;
			-d|--deb) Root_it /opt/Customizer/scripts/install_deb ;;
			-k|--hook) Root_it /opt/Customizer/scripts/hook ;;
			-g|--gui) Root_it /opt/Customizer/scripts/install_gui ;;
			-s|--snapshot) Root_it /opt/Customizer/scripts/create_snapshot ;;
			-i|--import) Root_it /opt/Customizer/scripts/import_snapshot ;;
			-r|--rebuild) Root_it /opt/Customizer/scripts/rebuild ;;
			-q|--qemu) Root_it /opt/Customizer/scripts/qemu ;;
			-t|--clean) Root_it /opt/Customizer/scripts/clean ;;
            -v|--version) Version ;;
			-h|--help) Usage ;;
			*) EXTRA_ERROR_MESSAGE "Unrecognized argument" "$arg" ;;
		esac
	done
else
	Usage
fi
	
