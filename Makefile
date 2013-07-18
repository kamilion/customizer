VERSION = 4.0.0
DESTDIR = 

all: static

static: clean
	mkdir -p build
	cd build && python2 ../pyinstaller/pyinstaller.py --strip --onefile --name=customizer --noconfirm ../src/main.py
	
install:
	install -vdm755 $(DESTDIR)/etc/ $(DESTDIR)/usr/sbin $(DESTDIR)/usr/share/customizer/
	install -vm755 build/dist/customizer $(DESTDIR)/usr/sbin/customizer
	install -vm644 data/customizer.conf $(DESTDIR)/etc/customizer.conf
	install -vm644 data/exclude.list $(DESTDIR)/usr/share/customizer/exclude.list

uninstall:
	$(RM) $(DESTDIR)/usr/sbin/customizer
	$(RM) $(DESTDIR)/etc/customizer.conf
	$(RM) $(DESTDIR)/usr/share/customizer/

bump:
	sed 's|^app_version.*|app_version = "$(VERSION)"|' -i src/lib/argparser.py
	git log > ChangeLog

dist: clean
	git archive HEAD --prefix=customizer-$(VERSION)/ | xz > customizer-$(VERSION).tar.xz

clean:
	$(RM) -r build $(shell find -name '*.pyc') *.tar.xz

.PHONY: all bump static install uninstall dist clean
