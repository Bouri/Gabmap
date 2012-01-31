VERSION=`git log --oneline|head -1|cut -d' ' -f1`
INCLUDES=`pkg-config --cflags glib-2.0`
CFLAGS=$(INCLUDES) -Wall -g 
LIBS=`pkg-config --libs glib-2.0`
LDLIBS=$(LIBS)

%_cmdline.c: %.ggo
	gengetopt --unamed-opts --set-version=$(VERSION) -i $^ -F $(^:%.ggo=%_cmdline)

%_cmdline.h: %.ggo
	gengetopt --unamed-opts --set-version=$(VERSION) -i $^ -F $(^:%.ggo=%_cmdline)

CSRCS=clusterdet.c clusterdet_cmdline.c strutils.c dist_matrix.c

COBJS=$(CSRCS:.c=.o)

OBJECTS=$(COBJS)
SRCS=$(CSRCS)



clusterdet: $(COBJS) 

depend: 
	$(CC) $(CFLAGS) -MM -MG $(SRCS) >.depend

clean:
	rm -f $(OBJECTS) *_cmdline.[ch] clusterdet

include .depend
