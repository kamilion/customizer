VERSION = 4.1.4 ($(REVISION))
REVISION = 
ifeq ($(wildcard .git), .git)
REVISION = $(shell $(GIT) rev-parse --short HEAD)
else
REVISION = $(shell echo "old stable")
endif

DESTDIR = 
PREFIX = $(shell $(PYTHON)-config --prefix)
ELEVATOR = pkexec
TRDIR =$(shell $(PYTHON) -c "from PyQt4.QtCore import QLibraryInfo; \
	print(QLibraryInfo.location(QLibraryInfo.TranslationsPath))")

PYTHON = python2
PYTHON_VERSION = $(shell $(PYTHON) -c "import sys; print(sys.version[:3])")
PYUIC = pyuic4
PYLUPDATE = pylupdate4 -noobsolete -verbose
LRELEASE = lrelease-qt4
RM = rm -vf
FIND = find
SED = sed
GREP = grep
INSTALL = install -v
GIT = git
XZ = xz -v
PYLINT = pylint
DPKG_BUILDPACKAGE = dpkg-buildpackage

all: clean core gui

core:
	$(SED) -e 's|@VERSION@|$(VERSION)|' -e 's|@PREFIX@|$(PREFIX)|g' \
		src/main.py.in > src/main.py

gui:
	$(SED) -e 's|@PREFIX@|$(PREFIX)|' -e 's|@ELEVATOR@|$(ELEVATOR)|' \
		data/customizer.menu.in > data/customizer.menu
	$(SED) -e 's|@PREFIX@|$(PREFIX)|' -e 's|@ELEVATOR@|$(ELEVATOR)|' \
		data/customizer.desktop.in > data/customizer.desktop
	$(SED) 's|@PREFIX@|$(PREFIX)|' data/customizer.policy.in > \
		data/customizer.policy
	$(SED) -e 's|@VERSION@|$(VERSION)|' -e 's|@PREFIX@|$(PREFIX)|g' \
		src/gui.py.in > src/gui.py
	$(PYUIC) src/gui.ui -o src/gui_ui.py
ifneq ($(shell which $(LRELEASE)),)
	$(PYLUPDATE) src/*.py -ts tr/*.ts
	$(LRELEASE) tr/*.ts
endif

install: install-core install-gui

install-core:
	$(INSTALL) -dm755 $(DESTDIR)/etc $(DESTDIR)$(PREFIX)/sbin \
		$(DESTDIR)$(PREFIX)/share/customizer/lib \
		$(DESTDIR)$(PREFIX)/share/customizer/actions
	$(INSTALL) -m755 src/main.py \
		$(DESTDIR)$(PREFIX)/sbin/customizer
	$(INSTALL) -m644 src/lib/*.py \
		$(DESTDIR)$(PREFIX)/share/customizer/lib/
	$(INSTALL) -m644 src/actions/*.py \
		$(DESTDIR)$(PREFIX)/share/customizer/actions/
	$(INSTALL) -m644 data/customizer.conf \
		$(DESTDIR)/etc/customizer.conf
	$(INSTALL) -m644 data/exclude.list \
		$(DESTDIR)$(PREFIX)/share/customizer/exclude.list

install-gui:
	$(INSTALL) -dm755 $(DESTDIR)$(PREFIX)/sbin \
		$(DESTDIR)$(PREFIX)/share/applications \
		$(DESTDIR)$(PREFIX)/share/customizer \
		$(DESTDIR)$(PREFIX)/share/menu \
		$(DESTDIR)$(PREFIX)/share/polkit-1/actions \
		$(DESTDIR)$(PREFIX)/share/icons/hicolor/24x24/apps \
		$(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps
	$(INSTALL) -m755 src/gui.py \
		$(DESTDIR)$(PREFIX)/sbin/customizer-gui
	$(INSTALL) -m644 src/gui_ui.py \
		$(DESTDIR)$(PREFIX)/share/customizer/
	$(INSTALL) -m644 data/customizer.desktop \
		$(DESTDIR)$(PREFIX)/share/applications/customizer.desktop
	$(INSTALL) -m644 data/logo.png \
		$(DESTDIR)$(PREFIX)/share/customizer/logo.png
	$(INSTALL) -m644 data/contributors \
		$(DESTDIR)$(PREFIX)/share/customizer/contributors
	$(INSTALL) -m644 debian/copyright \
		$(DESTDIR)$(PREFIX)/share/customizer/copyright
	$(INSTALL) -m644 data/customizer.menu \
		$(DESTDIR)$(PREFIX)/share/menu/customizer
	$(INSTALL) -m644 data/customizer.policy \
		$(DESTDIR)$(PREFIX)/share/polkit-1/actions/customizer.policy
	$(INSTALL) -m644 icons/customizer-24.png \
		$(DESTDIR)$(PREFIX)/share/icons/hicolor/24x24/apps/customizer.png
	$(INSTALL) -m644 icons/customizer-24.svg \
		$(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/customizer.svg
ifneq ($(shell which $(LRELEASE)),)
	$(INSTALL) -dm755 $(DESTDIR)$(TRDIR)/
	$(INSTALL) -m644 tr/*.qm $(DESTDIR)$(TRDIR)/
endif

uninstall:
	$(RM) $(DESTDIR)$(PREFIX)/sbin/customizer
	$(RM) $(DESTDIR)$(PREFIX)/sbin/customizer-gui
	$(RM) $(DESTDIR)/etc/customizer.conf
	$(RM) -r $(DESTDIR)$(PREFIX)/share/customizer/
	$(RM) $(DESTDIR)$(PREFIX)/share/applications/customizer.desktop
	$(RM) $(DESTDIR)$(PREFIX)/share/menu/customizer
	$(RM) $(DESTDIR)$(PREFIX)/share/polkit-1/actions/customizer.policy
	$(RM) $(DESTDIR)$(PREFIX)/share/icons/hicolor/24x24/apps/customizer.png
	$(RM) $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/customizer.svg

lint:
	cd src && $(PYLINT) lib/* actions/*.py main.py.in gui.py.in \
		| $(GREP) -v -e 'invalid syntax'

dist: clean
	$(GIT) archive HEAD --prefix="customizer-$(VERSION)/" | $(XZ) > \
		"customizer-$(VERSION).tar.xz"

changelog:
	$(GIT) log HEAD -n 1 --pretty='%cd %an <%ae> %n%H%d'
	$(GIT) log $(shell $(GIT) tag | tail -n1)..HEAD --no-merges --pretty='    * %s'

clean:
	$(RM) -r $(shell $(FIND) -name '*.pyc') tr/*.qm *.tar.xz
	$(RM) -r debian/*.log debian/customizer.substvars \
		debian/customizer debian/files \
		src/gui_ui.py src/gui.py src/main.py \
		data/customizer.policy data/customizer.menu \
		data/customizer.desktop

deb:
	DEB_BUILD_OPTIONS=nocheck $(DPKG_BUILDPACKAGE) -us -uc -b

.PHONY: all core gui install install-core install-gui uninstall lint dist changelog clean deb
