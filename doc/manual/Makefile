# Makefile for compiling and publishing pdfgui manual
# Available targets:
#
#   all      -- (default) build pdfgui manual in HTML and PDF formats
#   publish  -- upload the latest manual to www.diffpy.org
#   clean    -- remove intermediate texinfo files
#   cleanALL -- delete all generated files
#

all: pdfgui.pdf pdfgui.html

pdfgui.html: pdfgui.texinfo
	$(MAKE) -B -C images
	texi2html $<
	python extractEquations.py $<
	python fixHTMLCode.py $@

pdfgui.pdf: pdfgui.texinfo
	$(MAKE) -B -C images small
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

WEBDOCDIR = www.diffpy.org:/var/www/html/www.diffpy.org/doc/pdfgui

publish: all
	rsync -e /usr/bin/ssh -pRt --chmod=a+rwx,o-w,Dg+s,Fa-x \
	    pdfgui.html pdfgui.pdf images/*.png $(WEBDOCDIR)
