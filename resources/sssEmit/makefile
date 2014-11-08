# sssEmit 1.0 makefile

PREFIX=/usr

ECHO=@echo
MKDIR=mkdir -p
RM=rm -f
CP=cp -f

all:
	$(ECHO) "This package does not need to be built."

install:
	$(RM) -r $(PREFIX)/lib/blender/scripts/addons/sssEmit
	$(MKDIR) $(PREFIX)/lib/blender/scripts/addons/sssEmit
	$(CP) __init__.py $(PREFIX)/lib/blender/scripts/addons/sssEmit/
	$(CP) -r particle $(PREFIX)/lib/blender/scripts/addons/sssEmit/
	$(CP) -r scripts $(PREFIX)/lib/blender/scripts/addons/sssEmit/

clean:
	$(ECHO) "This package does not need to be cleaned."

