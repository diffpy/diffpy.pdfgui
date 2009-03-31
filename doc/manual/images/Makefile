# create links to the originals in good png or jpg format
# and convert them to pdf

CONVERT=cp
ifdef CONVERTARGS
	CONVERT = convert $(CONVERTARGS)
endif

# list of all generated images
IMAGECOPIES = \
    $(patsubst originals/%.png,%.png,$(wildcard originals/*.png)) \

images: $(IMAGECOPIES)

# make smaller images in 
small :
	CONVERTARGS='-geometry 425' $(MAKE) -B images

clean:
	/bin/rm -f -- *.png

# png to png
%.png: originals/%.png
	$(CONVERT) $< $@
