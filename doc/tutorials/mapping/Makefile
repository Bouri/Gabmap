LATEX=pdflatex -shell-escape #-interaction=batchmode
MAIN=mapping-tutorial
SOURCES=$(MAIN).tex
FIGURES=
SUBDIRS=images

.PHONY: all subdirs


all: $(MAIN).pdf

subdirs: 
	for dir in $(SUBDIRS); do  $(MAKE) -j 2 -C $$dir;  done

$(MAIN).pdf: subdirs $(SOURCES) $(FIGURES)
	$(LATEX) $(MAIN)
	$(LATEX) $(MAIN)
#	make -j 2 -f $(MAIN).makefile
	$(LATEX) $(MAIN)

$(MAIN).aux:
	pdflatex $(MAIN)

view:
	okular $(MAIN).pdf >/dev/null 2>&1 &

html: $(MAIN).html

$(MAIN).html: $(MAIN).pdf rex.cfg
#	htlatex $(MAIN) "rex,mathml,html,2" "" "-dhtml/"
	htlatex $(MAIN) "rex,mathml,html,2,uni-html4,charset=utf8" " -cunihtf -utf8" "" 

clean:
	rm -f *~ $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log\
		$(MAIN).pdf $(MAIN).snm $(MAIN).toc $(MAIN).nav $(MAIN).out 
