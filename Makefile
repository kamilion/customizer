VERSION = 4.1.0
DESTDIR = 
PYTHON = python2
PYTHON_VERSION = $(shell $(PYTHON) -c "import sys; print(sys.version[:3])")
PREFIX = $(shell $(PYTHON) -c "import sys; print(sys.prefix)")
NUITKA = $(PYTHON) ../nuitka/bin/nuitka --python-version=$(PYTHON_VERSION)
PYUIC = pyuic4
STRIP = strip
RM = rm -vf
PYCHECKER = $(PYTHON) ../pychecker/pychecker/checker.py

all: clean bump
	mkdir -p build
	$(PYUIC) src/gui.ui -o src/gui_ui.py
	cd build && $(NUITKA) --recurse-all ../src/main.py
	$(PYUIC) src/gui.ui -o src/gui_ui.py
	cd build && $(NUITKA) --recurse-all ../src/gui.py
	$(STRIP) build/main.exe build/gui.exe
	
install:
	install -vdm755 $(DESTDIR)/etc/ $(DESTDIR)$(PREFIX)/sbin \
		$(DESTDIR)$(PREFIX)/share/customizer/ \
		$(DESTDIR)$(PREFIX)/share/menu \
		$(DESTDIR)$(PREFIX)/share/applications
	install -vm755 build/main.exe $(DESTDIR)$(PREFIX)/sbin/customizer
	install -vm755 build/gui.exe $(DESTDIR)$(PREFIX)/sbin/customizer-gui
	install -vm644 data/customizer.conf $(DESTDIR)/etc/customizer.conf
	install -vm644 data/exclude.list $(DESTDIR)$(PREFIX)/share/customizer/exclude.list
	# install -vm644 data/customizer.desktop $(DESTDIR)$(PREFIX)/share/applications/customizer.desktop
	# install -vm644 data/customizer.menu $(DESTDIR)$(PREFIX)/share/menu/customizer

uninstall:
	$(RM) $(DESTDIR)$(PREFIX)/sbin/customizer
	$(RM) $(DESTDIR)$(PREFIX)/sbin/customizer-gui
	$(RM) $(DESTDIR)/etc/customizer.conf
	$(RM) -r $(DESTDIR)$(PREFIX)/share/customizer/
	$(RM) $(DESTDIR)$(PREFIX)/share/applications/customizer.desktop
	$(RM) $(DESTDIR)$(PREFIX)/share/menu/customizer
	
bump:
	sed 's|^app_version.*|app_version = "$(VERSION)"|' -i src/main.py src/gui.py

lint:
	pylint src/lib/* src/actions/*.py src/main.py | grep -v -e 'Line too long'

check: clean
	cd src && $(PYCHECKER) --limit=1000 lib/* actions/*.py

dist: clean
	git archive HEAD --prefix=customizer-$(VERSION)/ | xz > customizer-$(VERSION).tar.xz

clean:
	$(RM) -r build $(shell find -name '*.pyc') *.tar.xz

.PHONY: all bump static install uninstall dist clean
