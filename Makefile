VERSION = 4.0.0
DESTDIR = 
NUITKA = python2 ../nuitka/bin/nuitka
PYCHECKER = python2 ../pychecker/pychecker/checker.py

all: clean
	mkdir -p build
	cd build && $(NUITKA) --exe --recurse-all --verbose ../src/main.py
	
install:
	install -vdm755 $(DESTDIR)/etc/ $(DESTDIR)/usr/sbin $(DESTDIR)/usr/share/customizer/ \
		$(DESTDIR)/usr/share/menu $(DESTDIR)/usr/share/applications $(DESTDIR)/usr/share/customizer
	install -vm755 build/main.exe $(DESTDIR)/usr/sbin/customizer
	install -vm644 data/customizer.conf $(DESTDIR)/etc/customizer.conf
	install -vm644 data/exclude.list $(DESTDIR)/usr/share/customizer/exclude.list
	# install -vm644 data/customizer.desktop $(DESTDIR)/usr/share/applications/customizer.desktop
	# install -vm644 data/customizer.menu $(DESTDIR)/usr/share/menu/customizer

uninstall:
	$(RM) $(DESTDIR)/usr/sbin/customizer
	$(RM) $(DESTDIR)/etc/customizer.conf
	$(RM) -r $(DESTDIR)/usr/share/customizer/
	# $(RM) $(DESTDIR)/usr/share/applications/customizer.desktop
	# $(RM) $(DESTDIR)/usr/share/menu/customizer
	
bump:
	sed 's|^app_version.*|app_version = "$(VERSION)"|' -i src/lib/argparser.py

lint:
	cd src && pylint lib/configparser.py lib/message.py lib/misc.py actions/*.py \
		| grep -v -e 'Line too long'

check:
	cd src && $(PYCHECKER) --limit=1000 lib/configparser.py \
		lib/message.py lib/misc.py actions/*.py

dist: clean
	git archive HEAD --prefix=customizer-$(VERSION)/ | xz > customizer-$(VERSION).tar.xz

clean:
	$(RM) -r build $(shell find -name '*.pyc') *.tar.xz

.PHONY: all bump static install uninstall dist clean
