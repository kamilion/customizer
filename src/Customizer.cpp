//============================================================================
// Name        : Customizer.cpp
// Author      : SmiL3y
// Version     :
// Copyright   : Copyright (C) 2010-2012  Ivailo Monev
// Description : Hello World in C++, Ansi-style
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

	if (argc < 2)
		Usage();
	else
	{
	while ((arguments = getopt (argc, argv, "hv")) != -1)
	         switch (arguments)
	           {
	           case 'a':
	             cout << "called A" << endl;
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
	           }
	}
}
