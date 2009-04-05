# create links to the originals in png format
# When originals change, copy them in subversion as well.

# list of all generated images
IMAGECOPIES = \
    $(patsubst originals/%.png,%.png,$(wildcard originals/*.png))

images: $(IMAGECOPIES)

clean:
	/bin/rm -f -- *.png

# png files are the same as originals.  Since png files are
# also stored in subversion, perform svn copy when originals
# change.
%.png: originals/%.png
	ln -f -- $< $@
	if svn status $@ | grep -q '^[M?]'; then \
	    svn delete --force $@; \
	    svn copy $< $@; \
	fi
