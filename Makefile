all: dist

RESOURCE_PATH = pine_pass/gui/ui_definitions
GRESOURCE_XML_FILE = $(RESOURCE_PATH)/ui.gresource.xml
GRESOURCE_FILE = $(RESOURCE_PATH)/ui.gresource
GLIB_COMPILE_RESOURCES = glib-compile-resources --sourcedir=$(RESOURCE_PATH)


$(GRESOURCE_FILE): pine_pass/gui/ui_definitions/ui.gresource.xml $(shell $(GLIB_COMPILE_RESOURCES) --generate-dependencies $(GRESOURCE_XML_FILE))
	  $(shell $(GLIB_COMPILE_RESOURCES) $(GRESOURCE_XML_FILE))


resource: $(GRESOURCE_FILE)

dist: resource
	flit build

clean:
	rm -r dist
	rm $(GRESOURCE_FILE)