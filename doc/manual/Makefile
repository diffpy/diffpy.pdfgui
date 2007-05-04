all: images pdfgui.html pdfgui.pdf

.PHONY: images
images:
	$(MAKE) -C images

pdfgui.html: pdfgui.texinfo
	texi2html $<

pdfgui.pdf: pdfgui.texinfo
	texi2pdf $<

clean:
	/bin/rm -f -- \
	    pdfgui.vr pdfgui.tp pdfgui.pg pdfgui.ky pdfgui.fn \
	    pdfgui.cps pdfgui.cp pdfgui.toc pdfgui.aux pdfgui.log \
	    pdfgui.vrs

cleanALL: clean
	/bin/rm -f pdfgui.html pdfgui.pdf
