VERSION = 4.1.0
DESTDIR = 
PYTHON = python2
PYTHON_VERSION = $(shell $(PYTHON) -c "import sys; print(sys.version[:3])")
PREFIX = $(shell $(PYTHON) -c "import sys; print(sys.prefix)")
NUITKA = $(PYTHON) ../nuitka/bin/nuitka --python-version=$(PYTHON_VERSION)
PYUIC = pyuic4
STRIP = strip
RM = rm -vf
MKDIR = mkdir -vp
SED = sed
INSTALL = install -v
GIT = git
XZ = xz -v
PYCHECKER = $(PYTHON) ../pychecker/pychecker/checker.py
PYLINT = pylint
DEBUILD = debuild

all: clean core gui

core:
	$(MKDIR) build
	$(SED) 's|^app_version.*|app_version = "$(VERSION)"|' -i src/main.py
	cd build && $(NUITKA) --recurse-all ../src/main.py
	$(STRIP) build/main.exe

gui:
	$(MKDIR) build
	$(SED) 's|^app_version.*|app_version = "$(VERSION)"|' -i src/gui.py
	$(PYUIC) src/gui.ui -o src/gui_ui.py
	cd build && $(NUITKA) --recurse-all ../src/gui.py
	$(STRIP) build/gui.exe
	
install: install-core install-gui

install-core:
	$(INSTALL) -dm755 $(DESTDIR)/etc $(DESTDIR)$(PREFIX)/sbin \
		$(DESTDIR)$(PREFIX)/share/customizer
	$(INSTALL) -m755 build/main.exe $(DESTDIR)$(PREFIX)/sbin/customizer
	$(INSTALL) -m644 data/customizer.conf $(DESTDIR)/etc/customizer.conf
	$(INSTALL) -m644 data/exclude.list \
		$(DESTDIR)$(PREFIX)/share/customizer/exclude.list

install-gui:
	$(INSTALL) -dm755 $(DESTDIR)$(PREFIX)/sbin \
		$(DESTDIR)$(PREFIX)/share/applications \
		$(DESTDIR)$(PREFIX)/share/customizer \
		$(DESTDIR)$(PREFIX)/share/menu \
		$(DESTDIR)$(PREFIX)/share/polkit-1/actions
	$(INSTALL) -m755 build/gui.exe $(DESTDIR)$(PREFIX)/sbin/customizer-gui
	$(INSTALL) -m644 data/customizer.desktop \
		$(DESTDIR)$(PREFIX)/share/applications/customizer.desktop
	$(INSTALL) -m644 data/logo.png \
		$(DESTDIR)$(PREFIX)/share/customizer/logo.png
	$(INSTALL) -m644 data/customizer.menu \
		$(DESTDIR)$(PREFIX)/share/menu/customizer
	$(INSTALL) -m644 data/customizer.policy \
		$(DESTDIR)$(PREFIX)/share/polkit-1/actions/customizer.policy

uninstall:
	$(RM) $(DESTDIR)$(PREFIX)/sbin/customizer
	$(RM) $(DESTDIR)$(PREFIX)/sbin/customizer-gui
	$(RM) $(DESTDIR)/etc/customizer.conf
	$(RM) -r $(DESTDIR)$(PREFIX)/share/customizer/
	$(RM) $(DESTDIR)$(PREFIX)/share/applications/customizer.desktop
	$(RM) $(DESTDIR)$(PREFIX)/share/menu/customizer
	$(RM) $(DESTDIR)$(PREFIX)/share/polkit-1/actions/customizer.policy

lint:
	cd src && $(PYLINT) lib/* actions/*.py main.py | grep -v \
		-e 'Line too long'

check: clean
	cd src && $(PYCHECKER) --limit=1000 lib/* actions/*.py

dist: clean
	$(GIT) archive HEAD --prefix=customizer-$(VERSION)/ | $(XZ) > \
		customizer-$(VERSION).tar.xz

clean:
	$(RM) -r build $(shell find -name '*.pyc') *.tar.xz
	$(RM) -r debian/*.log debian/customizer.substvars \
		debian/customizer debian/files

deb:
	DEB_BUILD_OPTIONS=nocheck $(DEBUILD) -i -us -uc -b

.PHONY: all bump static install uninstall dist clean
