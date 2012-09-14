/*
 * clusterdet.c: Calculate cluster determinants.
 *
 * The aim of this utility is to provide a single interface for different
 * cluster determinants displayed by Gabmap. The current version only
 * implements a measure similar to Fisher's linear discriminant using
 * Levenshtein distances.
 *
 * Inputs: cluster information as output by RuG/L04 clgroup a set of distance
 * matrix files created by RuG/L04 leven
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>
#include <math.h>
#include <libgen.h>
#include <glib.h>
#include <assert.h>
#include "clusterdet.cmdline.h"
#include "strutils.h"
#include "dist_matrix.h"

struct options {
    int   inputn;       // number of input files
    char **input_files;
    char *output_file;
    int  debug;         // 0 quiet, 1 normal, >1 verbose
    char *clgroups;     // file to read cluster information from
    int  targetcl;      // the target cluster
    long  na_limit;
    double  na_rate;
    int norm;
    int diff;
} opt;


GHashTable *read_cllist(const char *fname, int **clcount, int *clmax);
void parse_cmdline(int argc, char **argv, struct options *opt);


int main(int argc, char **argv)
{
    int clmax;
    int *clcount = NULL;
    long na_limit_btw = 0, na_limit_wtn = 0;
    // process command line
    parse_cmdline(argc, argv, &opt);

    // read cluster info
    GHashTable *clusters = read_cllist(opt.clgroups, &clcount, &clmax);

//    if (opt.targetcl > clmax) {
//        fprintf(stderr, "Target cluster (%d) is not in `%s'.\n", 
//                opt.targetcl, opt.clgroups);
//        exit(1);
//    }

    // for each item
    int i;

//    for(i = 0; i <= clmax; i++) {
//        fprintf(stderr, "cl%d\t %d\n", i, clcount[i]);
//    }
    
    // warn here if target cluster is too small

    if (opt.na_limit == 0) {
        int M = clcount[opt.targetcl];
        int N = clcount[0];
        na_limit_wtn = lround(opt.na_rate * ((double)(M * M - M) / 2.0));
        na_limit_btw = lround(opt.na_rate * (N - M) * M);
    } else {
        na_limit_btw = na_limit_wtn = opt.na_limit;
    }


    for (i = 0; i < opt.inputn; i++) { // for each item (word)
        long count_within = 0,
             count_between = 0,
             count_all = 0,
             na_within = 0,
             na_between = 0;
        double ssd = 0.0,
               mean_all = 0.0;
        double dist_within = 0.0,
            dist_between = 0.0;
        // read item info
        struct dist_matrix *d = read_dist_matrix(opt.input_files[i]);

        // calculate derminant score for the item
        int j, k;
        for (j = 1; j < d->n; j++ ) { // for each location
            for (k = 0; k < j; k++ ) { // for each location, but avoid mult. comparisons
                int *clj = g_hash_table_lookup(clusters, d->labels[j]);
                int *clk = g_hash_table_lookup(clusters, d->labels[k]);
                assert (clj != NULL && clk != NULL);

                double dist = get_distance(d, j, k);

                if(!isnan(dist)) { // online variance calculation
                    double delta = dist - mean_all;
                    count_all++;
                    mean_all += delta/(double)count_all;
                    if (count_all > 1) ssd += delta * (dist - mean_all);
                }

                if (*clj != opt.targetcl && *clk != opt.targetcl) {
                    // irrelevant sites, useful only for normalization
                } else if (*clj == opt.targetcl && *clk == opt.targetcl) {
                    // both gropus are in target cluster: within
                    if (isnan(dist)) {
                        na_within++;
                    } else {
                        count_within++;
                        dist_within += dist;
                    }
                } else {
                    // one in one out: between
                    if (isnan(dist)) {
                        na_between++;
                    } else {
                        count_between++;
                        dist_between += dist;
                    }
                }
            }
        }

        double within_score, between_score, score;

//fprintf(stderr,"[dbg: %s] %ld:%ld / %ld ... %ld:%ld / %ld\n", opt.input_files[i], count_within, na_within, na_limit_wtn, count_between, na_between, na_limit_btw);
//fprintf(stderr,"[dbg] na_between: %ld / %ld\n\tna_within: %ld / %ld\n", na_between, na_limit_btw, na_within, na_limit_wtn);
        if(na_between > na_limit_btw ||
           na_within > na_limit_wtn) {
            within_score = between_score = score = NAN;
        } else {
            double sd_d = sqrt(ssd/(count_all-1));
            double avg_d_within = dist_within  / (double) count_within, 
                   avg_d_between = dist_between / (double) count_between;

            if(opt.norm) {
                within_score  = (avg_d_within - mean_all) / sd_d;
                between_score = (avg_d_between - mean_all) / sd_d;
            } else {
                within_score = avg_d_within;
                between_score = avg_d_between;
            }

            if (opt.norm || opt.diff) {
                score = between_score - within_score ;
            } else {
                score = (within_score == 0.0 && between_score == 0.0)
                      ? 1.0
                      : between_score / within_score ;
            }
        }

        // output the score
//        printf("%f\t%f\t%f\t%s\n", r, avg_d_within, avg_d_between,
        printf("%f\t%f\t%f\t%s\n", score , within_score, between_score,
                                   basename(opt.input_files[i]));
        // cleanup
        dist_matrix_free(d);
    }
    // cleanup
    g_hash_table_destroy(clusters);
    free(clcount);
    return 0;
}


/* read_clgroup(): read a cluster list prepared by RuG/L04 clgroup
 *                 into a hash table, and store the maximum cluster 
 *                 number in clmax. clcount is an array of integers 
 *                 with count of sites within each cluster number. 
 *                 clcount[0] is the total number of clusters.
 */
GHashTable *read_cllist(const char *fname, int **clcount, int *clmax)
{
    GHashTable *cllist = g_hash_table_new_full(g_str_hash, g_str_equal, free, free);;
    FILE *fp = fopen(fname, "r");
    char    buf[1024]; // TODO: make this dynamic
    int     cl_alloc = 64;
    int     *cbuf = calloc(cl_alloc, sizeof (*clcount));
    
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

            if(*cnum >= cl_alloc)  {
                cbuf = realloc(cbuf, (*clmax + 1) * sizeof (*cbuf));
                int i;
                for(i = cl_alloc+1; i <= *cnum ; i++) {
                    cbuf[i] = 0;
                }
                cl_alloc = *cnum + 1;
            }
            ++cbuf[*cnum];
            ++cbuf[0];
        }
        fgets(buf, 1024, fp);
    }

    *clcount = realloc(cbuf, (*clmax + 1) * sizeof (*clcount));
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

    opt->na_rate = 0.0;
    opt->na_limit = 0;

    if (ggo.ignore_na_arg > 1.0)  {
        opt->na_limit = lround(ggo.ignore_na_arg);
    } else {
        opt->na_rate = ggo.ignore_na_arg;
    }

    opt->diff = 0;
    if (ggo.diff_given) {
        opt->diff = 1;
    }

    opt->norm = 0;
    if (strcmp(ggo.normm_arg, "none")) {
        opt->norm = 1;
        opt->diff = 1;
    }

    cmdline_parser_free (&ggo);
}

