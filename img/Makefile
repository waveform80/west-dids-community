MAPS=council_map.svg \
     environ_agency_map.svg \
     nhw_map.svg \
     southway_map.svg \
     standard_map.svg \
     stats_map.svg

OPTIMIZED_MAPS=$(MAPS:%.svg=%.opt.svg)
PREVIEW_MAPS=$(MAPS:%.svg=%.jpg)

all: $(OPTIMIZED_MAPS) $(PREVIEW_MAPS) header.jpg

clean:
	rm -f $(MAPS:%.svg=%.png)

%.jpg: %.png
	convert -strip -interlace Plane -quality 75 -sampling-factor 4:2:0 $< $@

%.png: %.svg
	inkscape -C -w 2048 -e $@ $<

%.opt.svg: %.svg
	scour -i $< -o $@ --enable-id-stripping --enable-comment-stripping --shorten-ids --remove-metadata --indent=none

.PHONY: all clean
