# Build with:  make        Install with:  make install PREFIX=/usr/local
CC      ?= cc
PREFIX  ?= /usr/local
CFLAGS  ?= -O2
PKGS     = gtk4 libusb-1.0 fontconfig

# BLOCKS_DIR tells the binary where "make install" put the block editor.
brickcode-studio: brickcode-studio.c nqc_tables.inc i18n_es.inc bricks.inc .prefix
	$(CC) $(CFLAGS) -DBLOCKS_DIR='"$(PREFIX)/share/brickcode-studio/blocks"' \
	    $$(pkg-config --cflags $(PKGS)) -o $@ brickcode-studio.c \
	    $$(pkg-config --libs $(PKGS)) -lm

install: brickcode-studio
	install -Dm755 brickcode-studio $(DESTDIR)$(PREFIX)/bin/brickcode-studio
	for s in 48 64 128 256 512; do install -Dm644 icon-$$s.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/$${s}x$${s}/apps/brickcode-studio.png; done
	install -Dm644 brickcode-studio.desktop $(DESTDIR)$(PREFIX)/share/applications/brickcode-studio.desktop
	install -Dm644 brickcode-studio.svg $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/brickcode-studio.svg
	for f in ../firmware/*.lgo; do install -Dm644 $$f $(DESTDIR)$(PREFIX)/share/brickcode-studio/firmware/$$(basename $$f); done
	install -Dm644 ../blocks/brickcode-blocks.html $(DESTDIR)$(PREFIX)/share/brickcode-studio/blocks/brickcode-blocks.html
	install -Dm644 ../blocks/brickcode-blocks-rcx.html $(DESTDIR)$(PREFIX)/share/brickcode-studio/blocks/brickcode-blocks-rcx.html
	install -Dm644 ../blocks/brickcode-blocks-nxt.html $(DESTDIR)$(PREFIX)/share/brickcode-studio/blocks/brickcode-blocks-nxt.html
	install -Dm644 ../pybricks/pybricks-blocks.html $(DESTDIR)$(PREFIX)/share/brickcode-studio/blocks/pybricks-blocks.html
	install -Dm644 Orbitron-ExtraBold.ttf $(DESTDIR)$(PREFIX)/share/brickcode-studio/fonts/Orbitron-ExtraBold.ttf
	install -Dm644 Orbitron-OFL.txt $(DESTDIR)$(PREFIX)/share/brickcode-studio/fonts/Orbitron-OFL.txt
	for f in ../docs/USER_GUIDE.*.md; do install -Dm644 $$f $(DESTDIR)$(PREFIX)/share/brickcode-studio/docs/$$(basename $$f); done

# PREFIX is compiled into the binary (-DBLOCKS_DIR), so a build made for one
# prefix must not be installed into another. .prefix records the last one and
# changes only when PREFIX does, which forces the rebuild.
.PHONY: FORCE
FORCE:
.prefix: FORCE
	@[ -f $@ ] && [ "$$(cat $@)" = "$(PREFIX)" ] || echo "$(PREFIX)" > $@

clean:
	rm -f brickcode-studio .prefix
