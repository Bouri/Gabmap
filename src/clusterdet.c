/*
 * clusterdet.c: Calculate cluster determinants.
 *
 * The aim of this utility is to provide a single 
 * interface for different cluster determinants displayed
 * by Gabmap. The current version only implements a measure
 * similar to Fisher's linear discriminant using Levenshtein
 * distances.
 *
 * Inputs:
 *      cluster information as output by RuG/L04 clgroup
 *      a set of distance matrix files created by RuG/L04 leven
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>
#include <libgen.h>
#include <glib.h>
#include <assert.h>
#include "clusterdet_cmdline.h"
#include "strutils.h"
#include "dist_matrix.h"

struct options {
    int   inputn;       // number of input files
    char **input_files;
    char *output_file;
    int  debug;         // 0 quiet, 1 normal, >1 verbose
    char *clgroups;     // file to read cluster information from
    int  targetcl;      // the target cluster
} opt;


GHashTable *read_cllist(const char *fname, int *clmax);
void parse_cmdline(int argc, char **argv, struct options *opt);


int main(int argc, char **argv)
{
    int clmax;
    // process command line
    parse_cmdline(argc, argv, &opt);

    // read cluster info
    GHashTable *clusters = read_cllist(opt.clgroups, &clmax);

    if (opt.targetcl > clmax) {
        fprintf(stderr, "Target cluster (%d) is not in `%s'.\n", 
                opt.targetcl, opt.clgroups);
        exit(1);
    }

    // for each item
    int i;
    for (i = 0; i < opt.inputn; i++) { // for each item (word)
        int count_within = 0,
            count_between = 0;
        double dist_within = 0,
            dist_between = 0;
        // read item info
        struct dist_matrix *d = read_dist_matrix(opt.input_files[i]);

        // calculate derminant score for the item
        int j, k;
        for (j = 0; j < d->n; j++ ) { // for each location
            int *cl = g_hash_table_lookup(clusters, d->labels[j]);
            assert (cl != NULL);
            if (*cl != opt.targetcl) continue;

            for (k = 0; k < d->n; k++ ) { // for each location
                int *cl = NULL;
                cl = g_hash_table_lookup(clusters, d->labels[k]);
                if (cl == NULL) {
                    fprintf(stderr, "Not in any cluster? `%s'\n", d->labels[k]);
                    exit(1);
                }

                if (*cl == opt.targetcl) {
                    count_within++;
                    dist_within += get_distance(d, j, k);
                } else {
                    count_between++;
                    dist_between += get_distance(d, j, k);
                }
            }
        }

        double avg_d_within = dist_within / (double) count_within;
        double avg_d_between = dist_between / (double) count_between;
        double r = (avg_d_within == 0.0 && avg_d_between == 0.0)
                    ? 1.0
                    : avg_d_within / avg_d_between;
            
        // output the score
        printf("%f\t%f\t%f\t%s\n", r, avg_d_within, avg_d_between,
                                   opt.input_files[i]);
        // cleanup
        dist_matrix_free(d);
    }
    // cleanup
    g_hash_table_destroy(clusters);
    return 0;
}


/* read_clgroup(): read a cluster list prepared by RuG/L04 clgroup
 *                 into a hash table, and store the maximum cluster 
 *                 number in clmax
 *                 
 */
GHashTable *read_cllist(const char *fname, int *clmax)
{
    GHashTable *cllist = g_hash_table_new_full(g_str_hash, g_str_equal, free, free);;
    FILE *fp = fopen(fname, "r");
    char    buf[1024]; // TODO: make this dynamic

    if (!fp) {
        fprintf(stderr, "Cannot open file `%s'.\n", fname);
        exit(1);
    }

    *clmax = 0;
    fgets(buf, 1024, fp);
    while (!feof(fp)) {
        char    *location;
        int     *cnum = malloc(sizeof cnum);

        if (buf[0] != '#') {
            *cnum = atoi(strtok(buf, " \t"));
            location = strdup(str_strip(strtok(NULL, "\t\n\r"), " \""));
            g_hash_table_insert(cllist, location, cnum);
            if (*cnum > *clmax) *clmax = *cnum;
        }
        fgets(buf, 1024, fp);
    }

    fclose(fp);
    return cllist;
}


void parse_cmdline(int argc, char **argv, struct options *opt) 
{
    struct gengetopt_args_info ggo;

    if (cmdline_parser(argc, argv, &ggo) != 0) {
        cmdline_parser_print_version();
        cmdline_parser_print_help();
        exit(1);
    }

    if (ggo.inputs_num < 1) {
        fprintf(stderr, "At least one input file required\n");
        exit(1);
    }

    opt->input_files = malloc(ggo.inputs_num * sizeof (char *));

    unsigned i;

    for (i = 0; i < ggo.inputs_num; ++i) {
        opt->input_files[i] = strdup(ggo.inputs[i]);
    }
    opt->inputn = ggo.inputs_num;

    opt->debug = ggo.debug_arg;
    if (ggo.quiet_given) opt->debug = 0;
    opt->clgroups = strdup(ggo.clgroups_arg);
    opt->targetcl = ggo.cluster_arg;

    cmdline_parser_free (&ggo);
}

