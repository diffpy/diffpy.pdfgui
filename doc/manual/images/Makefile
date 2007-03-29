# create links to the originals in good png or jpg format
# and convert them to pdf

DENSITY = 72

# list of all generated images
IMAGECOPIES = \
    $(patsubst originals/%.png,%.png,$(wildcard originals/*.png)) \
    $(patsubst originals/%.png,%.pdf,$(wildcard originals/*.png)) \
    $(patsubst originals/%.jpg,%.jpg,$(wildcard originals/*.png)) \
    $(patsubst originals/%.jpg,%.pdf,$(wildcard originals/*.png)) \

images: $(IMAGECOPIES)

clean:
	/bin/rm -f -- *.png *.jpg *.pdf

# png to png
%.png: originals/%.png
	ln -s -- $< $@

# png to pdf
%.pdf: originals/%.png
	convert -density $(DENSITY) $< $@

# jpg to jpg
%.jpg: originals/%.jpg
	ln -sf -- $< $@

# jpg to pdf
%.pdf: originals/%.jpg
	convert -density $(DENSITY) $< $@
