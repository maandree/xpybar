PREFIX = /usr
BIN = /bin
DATA = /share
EXAMPLE = /share
BINDIR = $(PREFIX)$(BIN)
DATADIR = $(PREFIX)$(DATA)
EXAMPLEDIR = $(PREFIX)$(EXAMPLE)
LICENSEDIR = $(DATADIR)/licenses

PY3_SHEBANG = "/usr/bin/env python3"

COMMAND = xpybar
PKGNAME = xpybar
PLUGIN_PATH = $(DATADIR)/$(PKGNAME)

WARN = -Wall -Wextra -pedantic -Wdouble-promotion -Wformat=2 -Winit-self       \
       -Wmissing-include-dirs -Wtrampolines -Wfloat-equal -Wshadow             \
       -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls           \
       -Wnested-externs -Winline -Wno-variadic-macros -Wsign-conversion        \
       -Wswitch-default -Wconversion -Wsync-nand -Wunsafe-loop-optimizations   \
       -Wcast-align -Wstrict-overflow -Wdeclaration-after-statement -Wundef    \
       -Wbad-function-cast -Wcast-qual -Wwrite-strings -Wlogical-op            \
       -Waggregate-return -Wstrict-prototypes -Wold-style-definition -Wpacked  \
       -Wvector-operation-performance -Wunsuffixed-float-constants             \
       -Wsuggest-attribute=const -Wsuggest-attribute=noreturn                  \
       -Wsuggest-attribute=pure -Wsuggest-attribute=format -Wnormalized=nfkc


SRC = __main__ util x

PLUGINS = chase clock cpuinfo cpuonline cpu df discstats ipaddress  \
          kmsg leapsec linereader loadavg lunar mem moc network     \
          pacman snmp snmp6 softirqs solar uname uptime users       \
          vmstat weather xdisplay xkb alsa dentrystate inodestate   \
          files hdparm tzclock ropty ping inotify random swaps      \
          locks image application menu

PLUGIN_EXAMPLES = chase clock cpu cpuinfo cpuonline df discstats   \
                  ipaddress kmsg loadavg lunar mem moc network     \
                  pacman uname uptime users xdisplay xkb alsa      \
                  dentrystate inodestate files tzclock ropty ping  \
                  inotify random swaps locks image
# menu

TRICK_EXAMPLES = localutcclock anytzclock

EXAMPLES = mixed moderate test xmonad launchers



.PHONY: all
all: bin/xpybar bin/restricted-hdparm

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

bin/restricted-hdparm: obj/restricted-hdparm.o
	$(CC) -std=c89 -Ofast $(WARN) -o $@ $^

obj/%.o: src/%.c
	$(CC) -std=c89 -Ofast $(WARN) -c -o $@ $<


.PHONY: install
install: install-base

.PHONY: install-base
install-base: install-command install-license install-all-examples install-plugins

.PHONY: install-command
install-command: bin/xpybar bin/restricted-hdparm
	install -dm755                      -- "$(DESTDIR)$(BINDIR)"
	install -m755 bin/xpybar            -- "$(DESTDIR)$(BINDIR)/$(COMMAND)"
	install -m755 bin/restricted-hdparm -- "$(DESTDIR)$(BINDIR)/restricted-hdparm"

.PHONY: install-license
install-license: COPYING LICENSE.gpl3 LICENSE.agpl3
	install -dm755   -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"
	install -m644 $^ -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"

.PHONY: install-all-examples
install-all-examples: install-examples install-trick-examples install-plugin-examples

.PHONY: install-examples
install-examples: $(foreach F,$(EXAMPLES),examples/$(F))
	install -dm755   -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples"
	install -m644 $^ -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples"

.PHONY: install-trick-examples
install-trick-examples: $(foreach F,$(TRICK_EXAMPLES),examples/tricks/$(F))
	install -dm755   -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/tricks"
	install -m644 $^ -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/tricks"

.PHONY: install-plugin-examples
install-plugin-examples: $(foreach F,$(PLUGIN_EXAMPLES),examples/plugins/$(F))
	install -dm755   -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/plugins"
	install -m644 $^ -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/plugins"

.PHONY: install-plugins
install-plugins: $(foreach F,$(PLUGINS),src/plugins/$(F).py)
	install -dm755   -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/plugins"
	install -m644 $^ -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/plugins"



.PHONY: uninstall
uninstall:
	-rm -- "$(DESTDIR)$(BINDIR)/$(COMMAND)"
	-rm -- "$(DESTDIR)$(BINDIR)/restricted-hdparm"
	-rm -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)/COPYING"
	-rm -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)/LICENSE.gpl3"
	-rm -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)/LICENSE.agpl3"
	-rmdir -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"
	-rm -- $(foreach F,$(PLUGIN_EXAMPLES),"$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/plugins/$(F)")
	-rmdir -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/plugins"
	-rm -- $(foreach F,$(TRICK_EXAMPLES),"$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/tricks/$(F)")
	-rmdir -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/tricks"
	-rm -- $(foreach F,$(EXAMPLES),"$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/$(F)")
	-rmdir -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples"
	-rmdir -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)"
	-rm -- $(foreach F,$(PLUGINS),"$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins/$(F)")
	-rmdir -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins"
	-rmdir -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)"



.PHONY: clean
clean:
	-rm -r obj bin

