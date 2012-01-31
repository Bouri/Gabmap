#ifndef _DIST_MATRIX_H
#define _DIST_MATRIX_H       1

/* this structure defines a flat representation of a 2-D distancce matrix.
 * it is almost a literal representation of the 'Difference matrix file'
 * created by RuG/L04 leven
 */
struct dist_matrix {
    int n;
    char **labels;
    double *diff;
};

struct dist_matrix *read_dist_matrix(char *fname);
void dist_matrix_free(struct dist_matrix *d);
double get_distance(struct dist_matrix *d, int i, int j);

#endif // _DIST_MATRIX_H
