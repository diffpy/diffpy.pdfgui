# Makefile for compiling and publishing pdfgui manual
# Available targets:
#
#   all      -- (default) build pdfgui manual in HTML and PDF formats
#   clean    -- remove intermediate texinfo files
#   cleanALL -- delete all generated files
#   publish  -- copy the compiled manual files to WEBDIR directory
#
# Variables:
#
#   EQBUILD  -- extract PNG equations for HTML manual
#   WEBDIR   -- the rsync target directory.  Required by "publish" target.


all: pdfgui.pdf pdfgui.html


pdfgui.html: pdfgui.texinfo
	$(MAKE) -C images
	texi2html $<
ifdef EQBUILD
	python extractEquations.py $<
endif
	python fixHTMLCode.py $@


pdfgui.pdf: pdfgui.texinfo
	$(MAKE) -C images
	texi2pdf $<


clean:
	/bin/rm -f -- \
	    pdfgui.vr pdfgui.tp pdfgui.pg pdfgui.ky pdfgui.fn \
	    pdfgui.cps pdfgui.cp pdfgui.toc pdfgui.aux pdfgui.log \
	    pdfgui.vrs


cleanALL: clean
	/bin/rm -f pdfgui.html pdfgui.pdf
	$(MAKE) -C images clean


publish: all
ifndef WEBDIR
	$(error Set WEBDIR to define rsync target directory.)
endif
	rsync -pRt --chmod=a+rwx,go-w,Fa-x \
	    pdfgui.html pdfgui.pdf images/*.png $(WEBDIR)
