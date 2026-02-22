PREFIX     = /usr
BIN        = /bin
DATA       = /share
EXAMPLE    = /share
BINDIR     = $(PREFIX)$(BIN)
DATADIR    = $(PREFIX)$(DATA)
EXAMPLEDIR = $(PREFIX)$(EXAMPLE)
MANDIR     = $(DATADIR)/man
MAN1DIR    = $(MANDIR)/man1
INFODIR    = $(DATADIR)/info
DOCDIR     = $(DATADIR)/doc
LICENSEDIR = $(DATADIR)/licenses

PY3_SHEBANG = "/usr/bin/env python3"

CC       = c99
MAKEINFO = makeinfo
TEXI2DVI = texi2dvi

CPPFLAGS =
CFLAGS   =
LDFLAGS  =

HDPARM_PATH = /usr/sbin/hdparm

COMMAND     = xpybar
PKGNAME     = xpybar
PLUGIN_PATH = $(DATADIR)/$(PKGNAME)


SRC = __main__ util x

PLUGINS = chase clock cpuinfo cpuonline cpu df discstats ipaddress  \
          kmsg leapsec linereader loadavg lunar mem moc network     \
          pacman snmp snmp6 softirqs solar uname uptime users       \
          vmstat weather xdisplay xkb alsa dentrystate inodestate   \
          files hdparm tzclock ropty ping inotify random swaps      \
          locks image application menu ii powersupply lid

PLUGIN_EXAMPLES = chase clock cpu cpuinfo cpuonline df discstats   \
                  ipaddress kmsg loadavg lunar mem moc network     \
                  pacman uname uptime users xdisplay xkb alsa      \
                  dentrystate inodestate files tzclock ropty ping  \
                  inotify random swaps locks image
# menu

TRICK_EXAMPLES = localutcclock anytzclock

EXAMPLES = mixed moderate test xmonad launchers



.PHONY: default
default: base info shell

.PHONY: all
all: base doc shell

.PHONY: base
base: bin/xpybar bin/restricted-hdparm

bin/xpybar: obj/xpybar.zip
	mkdir -p bin
	echo "#!$(PY3_SHEBANG)" > $@
	cat obj/xpybar.zip >> $@
	chmod a+x $@

obj/xpybar.zip: $(foreach F,$(SRC),obj/$(F).py)
	cd obj && zip ../$@ $(foreach F,$(SRC),$(F).py)

obj/%.py: src/%.py
	mkdir -p obj
	cp  $< $@
	sed -i "s:PLUGIN_PATH = None:PLUGIN_PATH = '$(PLUGIN_PATH)':g" $@

bin/restricted-hdparm: obj/restricted-hdparm.o
	$(CC) -o $@ obj/restricted-hdparm.o $(LFDLAGS)

obj/%.o: src/%.c
	$(CC) -c -o $@ $< -D'HDPARM_PATH="$(HDPARM_PATH)"' $(CFLAGS) $(CPPFLAGS)

.PHONY: doc
doc: info pdf dvi ps

.PHONY: info
info: bin/xpybar.info
bin/%.info: doc/info/%.texinfo
	@mkdir -p bin
	$(MAKEINFO) $<
	mv $*.info $@

.PHONY: pdf
pdf: bin/xpybar.pdf
bin/%.pdf: doc/info/%.texinfo
	@! test -d obj/pdf || rm -rf obj/pdf
	@mkdir -p bin obj/pdf
	cd obj/pdf && texi2pdf ../../"$<" < /dev/null
	mv obj/pdf/$*.pdf $@

.PHONY: dvi
dvi: bin/xpybar.dvi
bin/%.dvi: doc/info/%.texinfo
	@! test -d obj/dvi || rm -rf obj/dvi
	@mkdir -p bin obj/dvi
	cd obj/dvi && $(TEXI2DVI) ../../"$<" < /dev/null
	mv obj/dvi/$*.dvi $@

.PHONY: ps
ps: bin/xpybar.ps
bin/%.ps: doc/info/%.texinfo
	@! test -d obj/ps || rm -rf obj/ps
	@mkdir -p bin obj/ps
	cd obj/ps && texi2pdf --ps ../../"$<" < /dev/null
	mv obj/ps/$*.ps $@

.PHONY: shell
shell: bash fish zsh

.PHONY: bash
bash: bin/xpybar.bash-completion

.PHONY: fish
fish: bin/xpybar.fish-completion

.PHONY: zsh
zsh: bin/xpybar.zsh-completion

obj/xpybar.auto-completion: src/xpybar.auto-completion
	@mkdir -p obj
	cp $< $@
	sed -i 's/^(xpybar/($(COMMAND)/' $@

bin/xpybar.%sh-completion: obj/xpybar.auto-completion
	@mkdir -p bin
	auto-auto-complete $*sh --output $@ --source $<



.PHONY: install
install: install-base install-info install-man install-shell

.PHONY: install-all
install-all: install-base install-doc install-shell

.PHONY: install-base
install-base: install-command install-license install-all-examples install-plugins

.PHONY: install-command
install-command: bin/xpybar bin/restricted-hdparm
	mkdir -p -- "$(DESTDIR)$(BINDIR)"
	cp -f -- bin/xpybar "$(DESTDIR)$(BINDIR)/$(COMMAND)"
	cp -f -- bin/restricted-hdparm "$(DESTDIR)$(BINDIR)/restricted-hdparm"

.PHONY: install-license
install-license: COPYING LICENSE.gpl3 LICENSE.agpl3
	mkdir -p -- "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"
	cp -f -- COPYING LICENSE.gpl3 LICENSE.agpl3 "$(DESTDIR)$(LICENSEDIR)/$(PKGNAME)"

.PHONY: install-all-examples
install-all-examples: install-examples install-trick-examples install-plugin-examples

.PHONY: install-examples
install-examples: $(foreach F,$(EXAMPLES),examples/$(F))
	mkdir -p -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples"
	cp -f -- $^ "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples"

.PHONY: install-trick-examples
install-trick-examples: $(foreach F,$(TRICK_EXAMPLES),examples/tricks/$(F))
	mkdir -p -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/tricks"
	cp -f -- $^ "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/tricks"

.PHONY: install-plugin-examples
install-plugin-examples: $(foreach F,$(PLUGIN_EXAMPLES),examples/plugins/$(F))
	mkdir -p -- "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/plugins"
	cp -f -- $^ "$(DESTDIR)$(EXAMPLEDIR)/$(PKGNAME)/examples/plugins"

.PHONY: install-plugins
install-plugins: $(foreach F,$(PLUGINS),src/plugins/$(F).py)
	mkdir -p -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins"
	cp -f -- $(foreach F,$(PLUGINS),src/plugins/$(F).py) "$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins"

.PHONY: install-doc
install-doc: install-info install-pdf install-dvi install-ps install-man

.PHONY: install-info
install-info: bin/xpybar.info
	mkdir -p -- "$(DESTDIR)$(INFODIR)"
	cp -f -- bin/xpybar.info "$(DESTDIR)$(INFODIR)/$(PKGNAME).info"

.PHONY: install-pdf
install-pdf: bin/xpybar.pdf
	mkdir -p -- "$(DESTDIR)$(DOCDIR)"
	cp -- bin/xpybar.pdf "$(DESTDIR)$(DOCDIR)/$(PKGNAME).pdf"

.PHONY: install-dvi
install-dvi: bin/xpybar.dvi
	mkdir -p -- "$(DESTDIR)$(DOCDIR)"
	cp -- bin/xpybar.dvi "$(DESTDIR)$(DOCDIR)/$(PKGNAME).dvi"

.PHONY: install-ps
install-ps: bin/xpybar.ps
	mkdir -p -- "$(DESTDIR)$(DOCDIR)"
	cp -- bin/xpybar.ps "$(DESTDIR)$(DOCDIR)/$(PKGNAME).ps"

.PHONY: install-man
install-man: doc/man/xpybar.1
	mkdir -p   -- "$(DESTDIR)$(MAN1DIR)"
	cp -- doc/man/xpybar.1 "$(DESTDIR)$(MAN1DIR)/$(COMMAND).1"

.PHONY: install-shell
install-shell: install-bash install-fish install-zsh

.PHONY: install-bash
install-bash: bin/xpybar.bash-completion
	mkdir -p -- "$(DESTDIR)$(DATADIR)/bash-completion/completions"
	cp -- bin/xpybar.bash-completion "$(DESTDIR)$(DATADIR)/bash-completion/completions/$(COMMAND)"

.PHONY: install-fish
install-fish: bin/xpybar.fish-completion
	mkdir -p -- "$(DESTDIR)$(DATADIR)/fish/completions"
	cp -- bin/xpybar.fish-completion "$(DESTDIR)$(DATADIR)/fish/completions/$(COMMAND).fish"

.PHONY: install-zsh
install-zsh: bin/xpybar.zsh-completion
	mkdir -p -- "$(DESTDIR)$(DATADIR)/zsh/site-functions"
	cp -- bin/xpybar.zsh-completion "$(DESTDIR)$(DATADIR)/zsh/site-functions/_$(COMMAND)"



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
	-rm -- $(foreach F,$(PLUGINS),"$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins/$(F).py")
	-rmdir -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)/plugins"
	-rmdir -- "$(DESTDIR)$(DATADIR)/$(PKGNAME)"
	-rm -- "$(DESTDIR)$(MAN1DIR)/$(COMMAND).1"
	-rm -- "$(DESTDIR)$(DATADIR)/bash-completion/completions/$(COMMAND)"
	-rm -- "$(DESTDIR)$(DATADIR)/fish/completions/$(COMMAND).fish"
	-rm -- "$(DESTDIR)$(DATADIR)/zsh/site-functions/_$(COMMAND)"
	-rm -- "$(DESTDIR)$(INFODIR)/$(PKGNAME).info"
	-rm -- "$(DESTDIR)$(DOCDIR)/$(PKGNAME).pdf"
	-rm -- "$(DESTDIR)$(DOCDIR)/$(PKGNAME).dvi"
	-rm -- "$(DESTDIR)$(DOCDIR)/$(PKGNAME).ps"



.PHONY: clean
clean:
	-rm -rf -- obj bin
