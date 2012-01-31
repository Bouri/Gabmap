/* 
 * strutils.c
 *
 * A set or utilities for easy string processing.
 *
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "strutils.h"


/* 
 * char *str_rstrip(char *s, char *rm)
 *      remove the characters in `rm' from the end of the string `s'.
 *      NOTE: these function modify the string in-place.
 */
char *
str_rstrip(char *s, const char *rm)
{
    size_t  n;
    char    *end;

    n = strlen(s);
    if (!n)
        return s;

    end = s + n - 1;
    while (end >= s && strchr(rm, *end))
        end--;
    *(end + 1) = '\0';

    return s;
}

/* 
 * char *str_lstrip(char *s, char *rm)
 *      remove the characters in `rm' from the beginning of the string `s'.
 */
char *
str_lstrip(char *s, const char *rm)
{
    while (*s && strchr(rm, *s))
        s++;
    return s;
}

/* 
 * char *str_strip(char *s, char *rm)
 *      remove the characters in `rm' from the beginning and the 
 *      end of the string `s'.
 */
char *
str_strip(char *s, const char *rm)
{

    s = str_lstrip(s, rm);
    s = str_rstrip(s, rm);

    return s;
}

/*
 * char *str_revn(char *s, unsigned n) 
 *      same as str_rev() except caller provides the length of the
 *      string.
 *
 */
char *
str_revn(char *s, unsigned n)
{
    char *tmp;
    int i;

    tmp = (char *)malloc(n+1);
    for(i=0;i<n;i++){
        tmp[i] = s[n-i-1];
    }
    tmp[n] = '\0';

    return tmp;
}

/*
 * char *str_rev(char *s) 
 *      returns the reverse of the given string s. memory for the returned  
 *      string is allocated, and has to be freed by the caller.
 */
char *
str_rev(char *s)
{
    return str_revn(s, strlen(s));
}


/*
 * char *str_revni(char *s, unsigned n) 
 *      same as str_revi() except caller provides the length of the
 *      string
 *
 */
char *
str_revni(char *s, unsigned n)
{
    char tmp;
    int  i;

    for(i=0;i<n/2;i++){
        tmp = s[i];
        s[i] = s[n-i-1];
        s[n-i-1] = tmp;
    }
    return s;
}

/*
 * char *str_revi(char *s) 
 *      string replacement is done `in-place'. retrun values is the
 *      address of the given string.
 */
char *
str_revi(char *s)
{
    return str_revni(s, strlen(s));
}

/* 
 * Remove a given character from a string
 * if the argument pos is not NULL, the address of an integer
 * array containing the indexes of the removed characters are placed
 * in pos.
 *
 * NOTE: this function modifies its string argument. If successful, 
 *       there will be some unused memory left after the string.
 *       strdup/free if necessary.
 */

char *
str_rmch(char *s, char ch, unsigned short **pos)
{
    char            *tmp = s;
    int             shift = 0, i = 0, j = 0;
    unsigned short  *tmpp = NULL, *ret = NULL;
    char chstr[2];

    if (pos) {
        tmpp = alloca(strlen(s) * sizeof(unsigned short));
        tmpp[0] = -1;
    }

    chstr[0] = ch; chstr[1] = '\0';
    str_strip(tmp, chstr);

    while(*tmp) {
        if(shift) *tmp = *(tmp + shift);
        if(*tmp == ch) {
            shift++;
            if (pos && (j == 0 || tmpp[j-1] != i)) {
                tmpp[j] = i;
                j++;
            }
        } else if (*tmp) {
            tmp++;
            i++;
        }
    }

    if(j) {
        ret = malloc((j+1)*sizeof(unsigned short));
        ret[0] = j;
        for(i=1; i <= j; i++){
            ret[i] = tmpp[i-1];
        }
        *pos = ret;
    } else if(pos) { 
        *pos = NULL;
    }
    return s;
}

/*
 * str_rmchs()
 * same as above. more than one characters given in `rm' 
 * prameter is removed
 *
 * FIXME: code is unnecessarily duplicated.
 */

char *
str_rmchs(char *s, const char *rm, unsigned short **pos)
{
    char            *tmp = s;
    int             shift = 0, i = 0, j = 0;
    unsigned short  *tmpp = NULL, *ret = NULL;

    if (pos) {
        tmpp = alloca(strlen(s) * sizeof(unsigned short));
        tmpp[0] = -1;
    }

    str_strip(tmp, rm);

    while(*tmp) {
        if(shift) *tmp = *(tmp + shift);

        if (strchr(rm, *tmp)) {
            shift++;
            if (pos && (j == 0 || tmpp[j-1] != i)) {
                tmpp[j] = i;
                j++;
            }
        } else if (*tmp) {
            tmp++;
            i++;
        }
    }

    if(j) {
        ret = malloc((j+1)*sizeof(unsigned short));
        ret[0] = j;
        for(i=1; i <= j; i++){
            ret[i] = tmpp[i-1];
        }
        *pos = ret;
    } else if(pos) { 
        *pos = NULL;
    }
    return s;
}

/* str_span()
 *
 * allocate and return the substring of length `length' 
 * starting at offset `start'
 */
char *
str_span(char *s, int start, int length)
{   
    char *ret = malloc(length+1);
    strncpy(ret, s + start, length);
    ret[length] = '\0';
    return ret;
}

/* str_rangecpy() - same as str_span() but copy over the provided string
 * 
 * the string dest should have space for at least length + 1 characters
 *
 */
char *
str_rangecpy(char *dest, char *src, int start, int length)
{
    strncpy(dest, src + start, length);
    dest[length] = '\0';
    return dest;
}

/* str_astrcat(char **dst, char *src);
 *
 * concatenates strings by re-allocating the memory if necessary
 *
 * first call allocates and assigns '*dst' to internal buffer
 * subsequent calls with the dst == NULL causes src to be appended 
 * to the buffer.
 *
 * calling with src = NULL will free the associated buffer. 
 * or the buffer allocated can be freed by the caller
 *
 * NOTE!: uses a static variables to store the size and the address 
 *        of the current buffer.
 *
 */
char *
str_astrcat(char **dst, char *src)
{
    static size_t   bufsize=0;
    static size_t   bufused=0;
    static char     *buf = NULL;
    size_t          n = strlen(src) + 1;

    if(src == NULL) {
        free(buf);
        buf = NULL;
        return NULL;
    }

    if(dst != NULL) {
        if (n < BUFSIZ) {
            bufsize = BUFSIZ;
        } else {
            bufsize = (n / BUFSIZ + 1) * BUFSIZ;
        }
        buf = calloc(bufsize, 1);
        bufused = n;
        strcpy(buf, src);
        *dst = buf;
    } else {
        int need = bufsize - (bufused + n);
        if (need > 0) {
            buf = realloc (buf, (need / BUFSIZ + 1) * BUFSIZ);
        }
        bufused += n;
        strcat(buf, src);
    }
    return buf;
}
