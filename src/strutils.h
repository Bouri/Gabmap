#ifndef _STRUTILS_H
#define _STRUTILS_H       1

char *str_span(char *s, int start, int length);
char *str_rangecpy(char *dest, char *src, int start, int length);


char *str_rev(char *s);
char *str_revn(char *s, unsigned n);
char *str_revi(char *s);
char *str_revni(char *s, unsigned n);

char *str_rmch(char *s, char ch, unsigned short **pos);
char *str_rmchs(char *s, const char *rm, unsigned short **pos);


char *str_lstrip(char *s, const char *rm);
char *str_rstrip(char *s, const char *rm);
char *str_strip(char *s, const char *rm);

char *str_astrcat(char **dst, char *src);


#endif // _STRUTILS_H 
