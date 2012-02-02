//============================================================================
// Name        : Customizer.cpp
// Author      : SmiL3y
// Version     :
// Copyright   : Copyright (C) 2010-2012  Ivailo Monev
// Description : Customizer - Advanced LiveCD Remastering Tool
//============================================================================

#include <iostream>
#include <getopt.h>
using namespace std;

int Version() {
	string ver = "4.0.0";
	string year = "2010-2012";
	string home_url = "https://github.com/fluxer/Customizer";
	string wiki_url = "https://github.com/fluxer/Customizer/wiki";
	string issues_url = "https://github.com/fluxer/Customizer/issues";

	cout << " Customizer v" << ver << "\n\n"

			" Customizer - Advanced LiveCD Remastering Tool\n"
			" Copyright (C) " << year << " Ivailo Monev\n\n"

			" Home: " << home_url << "\n"
			" Wiki: " << wiki_url << "\n"
			" Issues: " << issues_url << "\n\n"

			" Main developer:\n"
			"   Ivailo Monev (a.k.a SmiL3y)\n"
			"   <xakepa10@gmail.com>\n\n"

			" PPA maintainer:\n"
			"   Michał Głowienka (a.k.a. eloaders)\n"
			"   <eloaders@yahoo.com>\n\n"

			" Documentation:\n"
			"   Mubiin Kimura (a.k.a. clearkimura)\n"
			"   <clearkimura@gmail.com>\n" << endl;
	return 1;
}

int Usage() {
	string ver = "4.0.0";

	cout << " Customizer v" << ver << "\n\n"

			" Main options:\n\n"

			"     -e   Exctract ISO image\n"
			"     -c   Chroot into the filesystem\n"
			"     -x   Execute nested X-session\n"
			"     -p   Execute package manager\n"
			"     -d   Install Debian package\n"
			"     -k   Execute hook\n"
			"     -g   Install GUI (DE/WM)\n"
			"     -s   Creates snapshot of your current work\n"
			"     -i   Imports created snapshot\n"
			"     -r   Rebuild the ISO image\n"
			"     -q   Test the builded image with QEMU\n"
			"     -t   Clean all temporary files and folders\n\n"

			" Other options:\n\n"

			"     -h   Display this message\n"
			"     -v   Show the current version and more\n" << endl;
	return 1;
}

int main(int argc, char* argv[]) {
	int arguments;

	while ((arguments = getopt (argc, argv, "ecxpdkgsirqthv")) != -1)
	         switch (arguments)
	           {
	           case 'e':
	             cout << "EXTRACTING ISO" << endl;
	             break;
	           case 'c':
	           	 cout << "CHROOTING" << endl;
	           	 break;
	           case 'x':
	           	  cout << "NESTED-X" << endl;
	           	  break;
	           case 'p':
	        	   cout << "RUNNINIG PACKAGE MANAGER" << endl;
	        	   break;
	           case 'd':
	        	   cout << "INSTALLING DEB" << endl;
	        	   break;
	           case 'k':
	        	   cout << "EXECUTING HOOK" << endl;
	        	   break;
	           case 'g':
	        	   cout << "INSTALLING GUI" << endl;
	        	   break;
	           case 's':
	           	   cout << "CREATING SNAPSHOT" << endl;
	           	   break;
	           case 'i':
	           	   cout << "IMPORING SNAPSHOT" << endl;
	           	   break;
	           case 'r':
	        	   cout << "REBUILDING ISO" << endl;
	        	   break;
	           case 'q':
	        	   cout << "EMULATING ISO" << endl;
	        	   break;
	           case 't':
	        	   cout << "CLEANING UP" << endl;
	        	   break;
	           case 'h':
	        	 Usage();
	        	 break;
	           case 'v':
	        	 Version();
	        	 break;
	           case '?':
	        	 break;
	             return 1;
	           default:
	        	   Usage();
	        	   break;
	        	   return 1;
	           }
}
