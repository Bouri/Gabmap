/*
 * This utility reads in a matrix of the format used by Gabmap to store
 * numerical data, and outputs distances between location for each given item.
 * 
 * Input is a table of the form:
 *                  item1       item2   ...
 *  location1       val1,1      val1,2  ...
 *  location2       val2,1      val2,2  ...
 *  ...             ...         ...
 *
 * The output is multiple files in sparse difference-matrix format used 
 * by gabmap.
 */

#define _GNU_SOURCE // for getline() 
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <string.h>
#include <assert.h>
#include <math.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include "strutils.h"
#include "numdist.cmdline.h"

struct options {
    int normalize;
    char *output_dir;
    char *infile;
} opt;

struct numtable {
    int  nitems;
    int  nlabels;   // locations
    char **items;
    char **labels;
    double **data;
};

void parse_cmdline(int argc, char **argv, struct options *opt);
struct numtable *read_numtable(const char *fname);
void normalize_numtable(struct numtable *tbl);

char *fname_code(const char *s);
char *fname_decode(const char *s);

int main(int argc, char **argv)
{
    struct numtable *tbl;

    parse_cmdline(argc, argv, &opt);

    tbl = read_numtable(opt.infile);
    if (opt.normalize) {
        normalize_numtable(tbl);
    }

    struct stat sb;
    if (stat(opt.output_dir, &sb) == -1 && errno == ENOENT) {
        if (mkdir(opt.output_dir, 0755) == -1) {
            perror("mkdir");
            exit(EXIT_FAILURE);
        }
    } else if (!(S_ISDIR(sb.st_mode)
                 && (sb.st_mode & (S_IWUSR | S_IXUSR)))) {
        fprintf(stderr, "Cannot create output directory `%s'", opt.output_dir);
        exit(EXIT_FAILURE);
    }


    int i, loc1, loc2;
    for(i=0; i < tbl->nitems; i++) {
        char *fname = malloc(strlen(opt.output_dir) + 
                             strlen(tbl->items[i])*4 + 7);
        sprintf(fname, "%s/%s.diff", opt.output_dir, fname_code(tbl->items[i]));
        FILE *fp = fopen(fname, "w");
        fprintf(fp, "%d\n", tbl->nlabels);
        for(loc1 = 0; loc1 < tbl->nlabels; loc1++) {
            fprintf(fp, "%s\n", tbl->labels[loc1]);
        }
        for(loc1 = 1; loc1 < tbl->nlabels; loc1++) {
            for(loc2 = 0; loc2 < loc1; loc2++) {
                fprintf(fp, "%f\n", 
                        fabs(tbl->data[i][loc1] - tbl->data[i][loc2]));
            }
        }
        fclose(fp);
        free(fname);
    }

    // TODO: cleanup tbl
    return 0;
}



/* read_numtable() reads a file in Gabmap numeric data format, 
 * and returns the structure containing the data. The necessary 
 * memory allocated, it needs to be 'freed' by the caller.
 *
 */
struct numtable *read_numtable(const char *fname)
{
    FILE *fp = fopen(fname, "r");
    char *line = NULL;
    size_t buflen = 0;
    size_t nread = 0;
    int  i;
    struct numtable *tbl;

    if(!fp) {
        fprintf(stderr, "Cannot open input file `%s'\n", fname);
        exit(1);
    }


    tbl = malloc(sizeof (*tbl));
    nread = getline(&line, &buflen, fp);
    while(line[0] == '#' || line[0] == '\r' || line[0] == '\n') {
        nread = getline(&line, &buflen, fp);
printf("%s\n", line);
    }
    assert(nread > 0);


    char *tok = strtok(line, "\t\n\r");
    tbl->nitems = 0;
//    if (line[0] != '\t') {
//        tok = strtok(NULL, "\t\n\r");
//    }
    int itemalloc = 1024;
    tbl->items = malloc(itemalloc * sizeof *tbl->items);
    while(tok) {
        if(tbl->nitems >= itemalloc) {
            itemalloc += 1024;
            tbl->items = realloc(tbl->items, itemalloc * sizeof (*tbl->items));
        }
        tbl->items[tbl->nitems] = strdup(str_strip(tok, " \"\t\n"));
        ++tbl->nitems;
        tok = strtok(NULL, "\t\n\r");
    }


    tbl->data = malloc((tbl->nitems + 1) * sizeof (*tbl->data));

    int labelalloc = 1024;
    tbl->labels = malloc(labelalloc * sizeof *tbl->labels);
    for (i=0; i < tbl->nitems; i++) {
        tbl->data[i] = malloc(labelalloc * sizeof (**tbl->data));
    }
    tbl->nlabels = 0;

    while((nread = getline(&line, &buflen, fp)) != -1) {
        if(line[0] == '#' || line[0] == '\r' || line[0] == '\n') {
            continue;
        }
        int item = 0;
        if(tbl->nlabels >= itemalloc) {
            labelalloc += 1024;
            tbl->labels = realloc(tbl->labels, 
                                  itemalloc * sizeof (*tbl->labels));
            for (i=0; i < tbl->nitems; i++) {
                tbl->data[i] = malloc(labelalloc * sizeof (**tbl->data));
            }
        }

        char *tok = strtok(line, "\t\n\r");
        tbl->labels[tbl->nlabels] = strdup(str_strip(tok, " \"\t\n"));

        tok = strtok(NULL, "\t\n\r");
        while(tok) {
            if (!strncmp(tok, "NA", 2)) {
                tbl->data[item][tbl->nlabels] = NAN;
            } else {
                tbl->data[item][tbl->nlabels] = atof(tok);
            }
            ++item;
            tok = strtok(NULL, "\t\n\r");
        }
        ++tbl->nlabels;
    }

    free(line);
    return tbl;
}

/* normalize_numtable() replaces the data in the table with 
 * normalized values (z-scores).
 */
void normalize_numtable(struct numtable *tbl)
{
    int i;

    for (i=0; i < tbl->nitems; i++) {
        // pass 1: calculate the mean
        size_t n = 0;
        double sum = 0.0;
        int loc;
        for(loc=0; loc < tbl->nlabels; loc++) {
            if(!isnan(tbl->data[i][loc])) {
                n++;
                sum += tbl->data[i][loc];
            }
        }
        if (n == 0) continue; // there is no data to normalize
        double mean = sum / (double) n;

        // pass 2: calculate the standard deviation
        double sum2 = 0.0;
        for(loc=0; loc < tbl->nlabels; loc++) {
            if(!isnan(tbl->data[i][loc])) {
                sum2 += (tbl->data[i][loc] - mean) * (tbl->data[i][loc] - mean);
            }
        }
        double sd = sqrt(sum2 / (double) n);

        // pass 3: update the data
        for(loc=0; loc < tbl->nlabels; loc++) {
            if(!isnan(tbl->data[i][loc])) {
                tbl->data[i][loc] = (tbl->data[i][loc] - mean) / sd;
            }
        }
    }
}


void parse_cmdline(int argc, char **argv, struct options *opt) 
{
    struct gengetopt_args_info ggo;

    if (cmdline_parser(argc, argv, &ggo) != 0) {
        cmdline_parser_print_version();
        cmdline_parser_print_help();
        exit(1);
    }


/*
    opt->input_files = malloc(ggo.inputs_num * sizeof (char *));

    unsigned i;

    for (i = 0; i < ggo.inputs_num; ++i) {
        opt->input_files[i] = strdup(ggo.inputs[i]);
    }
    opt->inputn = ggo.inputs_num;

*/

    if (ggo.inputs_num == 0) {
        opt->infile = "../data/table.txt";
    } else {
        opt->infile = strdup(ggo.inputs[0]);
    }

    opt->output_dir = strdup(ggo.output_dir_arg);

    opt->normalize = 0;
    if (strcmp(ggo.norm_arg, "none")) {
        opt->normalize = 1;
    }

    cmdline_parser_free (&ggo);
}


/* fnmae_code() replaces non-alphanumeric (or +, -) characters 
 * with _NUM_ where NUM is the numeric 
 */
char *fname_code(const char *s)
{
    char *tmp = malloc(4*strlen(s));
    const char *ch; 
    char *ret;
    int i;

    ch = s;

    i = 0;
    while(*ch) {
        if (*ch == '/') {
            strcat(tmp, "_47_");
            i += 4;
        } else {
            tmp[i] = *ch;
            tmp[i+1] = '\0';
            i++;
        }
        ch++;
    }

    ret = strdup(tmp);
    free(tmp);
    return ret;
}

char *fname_decode(const char *s)
{
    char *tmp = strdup(s);
    char *ch;

    ch = tmp;
    while((ch = strstr(tmp, "_47_"))) {
        char *c = ch + 4;
        *ch = '/';
        *(c-3) = *c;
        while (*c) {
            c++;
            *(c-3) = *c;
        }
    }

    return(tmp);
}

