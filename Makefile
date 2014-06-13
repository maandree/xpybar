PREFIX ?= /usr
BIN ?= /bin
BINDIR ?= $(PREFIX)$(BIN)
DATA ?= /share
DATADIR ?= $(PREFIX)$(DATA)
DOC ?= /share
DOCDIR ?= $(PREFIX)$(DOC)
LICENSEDIR ?= $(DATADIR)/licenses

PY3_SHEBANG = "/usr/bin/env python3"

COMMAND = xpybar
PKGNAME = xpybar
PLUGIN_PATH = $(DATADIR)/$(PKGNAME)


SRC = __main__ util x

PLUGINS = chase clock cpuifo cpuonline cpu df discstats ipaddress  \
          leapsec linereader loadavg lunar mem moc network pacman  \
          snmp snmp6 softirqs solar uname uptime users vmstat      \
          weather xdisplay xkb

PLUGIN_EXAMPLES = chase clock cpu cpuinfo cpuonline df discstats   \
                  ipaddress loadavg lunar mem moc network pacman   \
                  uname uptime users xdisplay xkb

EXAMPLES = clock mixed moderate plugin-test test xmonad



.PHONY: all
all: bin/xpybar

bin/xpybar: obj/xpybar.zip
	mkdir -p bin
	echo "#!$(PY3_SHEBANG)" > $@
	cat $< >> $@
	chmod a+x $@

obj/xpybar.zip: $(foreach F,$(SRC),obj/$(F).py)
	cd obj && zip ../$@ $(foreach F,$(SRC),$(F).py)

obj/%.py: src/%.py
	mkdir -p obj
	cp $< $@
	sed -i "s:PLUGIN_PATH = None:PLUGIN_PATH = '$(PLUGIN_PATH)':g" $@



.PHONY: install
install: install-base

.PHONY: install-base
install-base: install-command install-license install-all-examples install-plugins

.PHONY: install-command
install-command: bin/xpybar
	install -dm755   -- "$(DESTDIR)$(BINDIR)"
	install -m755 $< -- "$(DESTDIR)$(BINDIR)/$(COMMAND)"

.PHONY: install-license
install-license: COPYING LICENSE.gpl3 LICENSE.agpl3
	install -dm755   -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"
	install -m644 $^ -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"

.PHONY: install-all-examples
install-all-examples: install-examples install-plugin-examples

.PHONY: install-examples
install-examples: $(foreach F,$(EXAMPLES),examples/$(F))
	install -dm755   -- "$(DESTDIR)$(DOCDIR)/$(PKGNAME)/examples"
	install -m644 $^ -- "$(DESTDIR)$(DOCDIR)/$(PKGNAME)/examples"

.PHONY: install-plugin-examples
install-plugin-examples: $(foreach F,$(PLUGIN_EXAMPLES),examples/plugins/$(F))
	install -dm755   -- "$(DESTDIR)$(DOCDIR)/$(PKGNAME)/examples/plugins"
	install -m644 $^ -- "$(DESTDIR)$(DOCDIR)/$(PKGNAME)/examples/plugins"

.PHONY: install-plugins
install-plugins: $(foreach F,$(PLUGINS),src/plugins/$(F).py)
	install -dm755   -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins"
	install -m644 $^ -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins"



.PHONY: uninstall
uninstall:
	-rm -- "$(DESTDIR)$(BINDIR)/$(COMMAND)"
	-rm -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)/COPYING"
	-rm -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)/LICENSE.gpl3"
	-rm -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)/LICENSE.agpl3"
	-rmdir -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"
	-rm -- $(foreach F,$(PLUGIN_EXAMPLES),"$(DESTDIR)$(DOCDIR)/$(PKGNAME)/examples/plugins/$(F)")
	-rmdir -- "$(DESTDIR)$(DOCDIR)/$(PKGNAME)/examples/plugins"
	-rm -- $(foreach F,$(EXAMPLES),"$(DESTDIR)$(DOCDIR)/$(PKGNAME)/examples/$(F)")
	-rmdir -- "$(DESTDIR)$(DOCDIR)/$(PKGNAME)/examples"
	-rmdir -- "$(DESTDIR)$(DOCDIR)/$(PKGNAME)"
	-rm -- $(foreach F,$(PLUGINS),"$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins/$(F)")
	-rmdir -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins"
	-rmdir -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)"



.PHONY: clean
clean:
	-rm -r obj bin

