VERSION=`git log --oneline|head -1|cut -d' ' -f1`
PYTHON3=/usr/bin/python3.2

INCLUDES=`pkg-config --cflags glib-2.0`
CFLAGS=-std=gnu99 -Wall -g $(INCLUDES)
LIBS=`pkg-config --libs glib-2.0` -lm
LDLIBS=$(LIBS)

EXEC=clusterdet count_forms formstorgb makelongtip
BINDIR=../util

%.cmdline.c: %.ggo
	gengetopt --unamed-opts --set-version=$(VERSION) -i $^ -F $(^:%.ggo=%.cmdline)

%.cmdline.h: %.ggo
	gengetopt --unamed-opts --set-version=$(VERSION) -i $^ -F $(^:%.ggo=%.cmdline)

CSRCS=clusterdet.c strutils.c dist_matrix.c

COBJS=$(CSRCS:.c=.o) clusterdet.cmdline.o

OBJECTS=$(COBJS)
SRCS=$(CSRCS)

all: $(EXEC)

clusterdet: $(COBJS) 

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
