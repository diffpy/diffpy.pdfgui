# Makefile for compiling and publishing pdfgui manual
# Available targets:
#
#   all      -- (default) build pdfgui manual in HTML and PDF formats
#   publish  -- upload the latest manual to www.diffpy.org
#   clean    -- remove intermediate texinfo files
#   cleanALL -- delete all generated files
#

all: images pdfgui.html pdfgui.pdf

.PHONY: images
images:
	$(MAKE) -C images

pdfgui.html: pdfgui.texinfo
	texi2html $<
	python extractEquations.py $<
	python fixHTMLCode.py $@

pdfgui.pdf: pdfgui.texinfo
	texi2pdf $<

clean:
	/bin/rm -f -- \
	    pdfgui.vr pdfgui.tp pdfgui.pg pdfgui.ky pdfgui.fn \
	    pdfgui.cps pdfgui.cp pdfgui.toc pdfgui.aux pdfgui.log \
	    pdfgui.vrs pdfgui.html
	/bin/rm -f -- images/eq-*.png

cleanALL: clean
	/bin/rm -f pdfgui.html pdfgui.pdf
	$(MAKE) -C images clean

WEBDOCDIR = www.diffpy.org:/var/www/html/diffpy/doc/pdfgui

publish: all
	rsync -e /usr/bin/ssh -pRt --chmod=a+rwx,o-w,Dg+s,Fa-x \
	    pdfgui.html pdfgui.pdf images/*.png $(WEBDOCDIR)
