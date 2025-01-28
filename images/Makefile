# create links to the originals in png format
# When originals change, copy them in subversion as well.

# list of all generated images
IMAGECOPIES = \
    $(patsubst originals/%.png,%.png,$(wildcard originals/*.png))

images: $(IMAGECOPIES)

clean:
	/bin/rm -f -- *.png

# png files are the same as originals.
%.png: originals/%.png
	ln -f -- $< $@
