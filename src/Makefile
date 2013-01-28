VERSION=$(shell git log --oneline|head -1|cut -d' ' -f1)
PYTHON3=$(shell which python3)
PYTHON2=$(shell which python2.6)

INCLUDES=$(shell pkg-config --cflags glib-2.0)
CFLAGS=-std=gnu99 -Wall -g $(INCLUDES)
LIBS=$(shell pkg-config --libs glib-2.0) -lm
LDLIBS=$(LIBS)

EXEC=clusterdet count_forms formstorgb makelongtip numdist
BINDIR=../util

%.cmdline.c: %.ggo
	gengetopt --unamed-opts --set-version=$(VERSION) -i $^ -F $(^:%.ggo=%.cmdline)

%.cmdline.h: %.ggo
	gengetopt --unamed-opts --set-version=$(VERSION) -i $^ -F $(^:%.ggo=%.cmdline)

CLUDET_SRCS=clusterdet.c strutils.c dist_matrix.c

NUMDIST_SRCS=numdist.c strutils.c

CLUDET_OBJ=$(CLUDET_SRCS:.c=.o) clusterdet.cmdline.o
NUMDIST_OBJ=$(NUMDIST_SRCS:.c=.o) numdist.cmdline.o

OBJECTS=$(CLUDET_OBJ) $(NUMDIST_OBJ)
SRCS=$(CLUDET_SRCS) $(NUMDIST_SRCS)

all: $(EXEC)

clusterdet: $(CLUDET_OBJ) 

numdist: $(NUMDIST_OBJ) 

depend: 
	$(CC) $(CFLAGS) -MM -MG $(SRCS) >.depend

clean:
	rm -f $(OBJECTS) *.cmdline.[ch] clusterdet

include .depend

count_forms: count_forms.py
	sed s,__PYTHON3__,$(PYTHON3),g $^ > $@
	chmod 755 $@

formstorgb: formstorgb.py
	sed s,__PYTHON3__,$(PYTHON3),g $^ > $@
	chmod 755 $@

makelongtip: makelongtip.py
	sed s,__PYTHON3__,$(PYTHON3),g $^ > $@
	chmod 755 $@

install:
	cp $(EXEC) $(BINDIR)

include .depend

.INTERMEDIATE:
.SECONDARY:
