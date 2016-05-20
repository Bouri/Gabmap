/** @file clusterdet.cmdline.h
 *  @brief The header file for the command line option parser
 *  generated by GNU Gengetopt version 2.22.6
 *  http://www.gnu.org/software/gengetopt.
 *  DO NOT modify this file, since it can be overwritten
 *  @author GNU Gengetopt by Lorenzo Bettini */

#ifndef CLUSTERDET_CMDLINE_H
#define CLUSTERDET_CMDLINE_H

/* If we use autoconf.  */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <stdio.h> /* for FILE */

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

#ifndef CMDLINE_PARSER_PACKAGE
/** @brief the program name (used for printing errors) */
#define CMDLINE_PARSER_PACKAGE "clusterdet"
#endif

#ifndef CMDLINE_PARSER_PACKAGE_NAME
/** @brief the complete program name (used for help and version) */
#define CMDLINE_PARSER_PACKAGE_NAME "clusterdet"
#endif

#ifndef CMDLINE_PARSER_VERSION
/** @brief the program version */
#define CMDLINE_PARSER_VERSION "44a52b0"
#endif

/** @brief Where the command line options are stored */
struct gengetopt_args_info
{
  const char *help_help; /**< @brief Print help and exit help description.  */
  const char *version_help; /**< @brief Print version and exit help description.  */
  int debug_arg;	/**< @brief debug level. --quiet overrides (default='1').  */
  char * debug_orig;	/**< @brief debug level. --quiet overrides original value given at command line.  */
  const char *debug_help; /**< @brief debug level. --quiet overrides help description.  */
  const char *quiet_help; /**< @brief be quiet, same as --debug=0 help description.  */
  char * output_arg;	/**< @brief output file name (default='-').  */
  char * output_orig;	/**< @brief output file name original value given at command line.  */
  const char *output_help; /**< @brief output file name help description.  */
  char * clgroups_arg;	/**< @brief file to read cluster groups (default='clgroups.txt').  */
  char * clgroups_orig;	/**< @brief file to read cluster groups original value given at command line.  */
  const char *clgroups_help; /**< @brief file to read cluster groups help description.  */
  int cluster_arg;	/**< @brief number of the target cluster.  */
  char * cluster_orig;	/**< @brief number of the target cluster original value given at command line.  */
  const char *cluster_help; /**< @brief number of the target cluster help description.  */
  char * normm_arg;	/**< @brief normlize scores (default='none').  */
  char * normm_orig;	/**< @brief normlize scores original value given at command line.  */
  const char *normm_help; /**< @brief normlize scores help description.  */
  const char *gmean_help; /**< @brief use geometric mean of 'between' and 'within' scores ad aggregate score (overrides --diff) help description.  */
  const char *diff_help; /**< @brief take the difference of between/wtihin score instead of division (implied by --norm) help description.  */
  float ignore_na_arg;	/**< @brief maximum number or ratio of the NA's values to tolerate while calculating averages.
  If the argument is in range [0,1] it is interpreted as a ratio,otherwise it is taken as an absolute count value. (default='0').  */
  char * ignore_na_orig;	/**< @brief maximum number or ratio of the NA's values to tolerate while calculating averages.
  If the argument is in range [0,1] it is interpreted as a ratio,otherwise it is taken as an absolute count value. original value given at command line.  */
  const char *ignore_na_help; /**< @brief maximum number or ratio of the NA's values to tolerate while calculating averages.
  If the argument is in range [0,1] it is interpreted as a ratio,otherwise it is taken as an absolute count value. help description.  */
  
  unsigned int help_given ;	/**< @brief Whether help was given.  */
  unsigned int version_given ;	/**< @brief Whether version was given.  */
  unsigned int debug_given ;	/**< @brief Whether debug was given.  */
  unsigned int quiet_given ;	/**< @brief Whether quiet was given.  */
  unsigned int output_given ;	/**< @brief Whether output was given.  */
  unsigned int clgroups_given ;	/**< @brief Whether clgroups was given.  */
  unsigned int cluster_given ;	/**< @brief Whether cluster was given.  */
  unsigned int normm_given ;	/**< @brief Whether normm was given.  */
  unsigned int gmean_given ;	/**< @brief Whether gmean was given.  */
  unsigned int diff_given ;	/**< @brief Whether diff was given.  */
  unsigned int ignore_na_given ;	/**< @brief Whether ignore-na was given.  */

  char **inputs ; /**< @brief unamed options (options without names) */
  unsigned inputs_num ; /**< @brief unamed options number */
} ;

/** @brief The additional parameters to pass to parser functions */
struct cmdline_parser_params
{
  int override; /**< @brief whether to override possibly already present options (default 0) */
  int initialize; /**< @brief whether to initialize the option structure gengetopt_args_info (default 1) */
  int check_required; /**< @brief whether to check that all required options were provided (default 1) */
  int check_ambiguity; /**< @brief whether to check for options already specified in the option structure gengetopt_args_info (default 0) */
  int print_errors; /**< @brief whether getopt_long should print an error message for a bad option (default 1) */
} ;

/** @brief the purpose string of the program */
extern const char *gengetopt_args_info_purpose;
/** @brief the usage string of the program */
extern const char *gengetopt_args_info_usage;
/** @brief the description string of the program */
extern const char *gengetopt_args_info_description;
/** @brief all the lines making the help output */
extern const char *gengetopt_args_info_help[];

/**
 * The command line parser
 * @param argc the number of command line options
 * @param argv the command line options
 * @param args_info the structure where option information will be stored
 * @return 0 if everything went fine, NON 0 if an error took place
 */
int cmdline_parser (int argc, char **argv,
  struct gengetopt_args_info *args_info);

/**
 * The command line parser (version with additional parameters - deprecated)
 * @param argc the number of command line options
 * @param argv the command line options
 * @param args_info the structure where option information will be stored
 * @param override whether to override possibly already present options
 * @param initialize whether to initialize the option structure my_args_info
 * @param check_required whether to check that all required options were provided
 * @return 0 if everything went fine, NON 0 if an error took place
 * @deprecated use cmdline_parser_ext() instead
 */
int cmdline_parser2 (int argc, char **argv,
  struct gengetopt_args_info *args_info,
  int override, int initialize, int check_required);

/**
 * The command line parser (version with additional parameters)
 * @param argc the number of command line options
 * @param argv the command line options
 * @param args_info the structure where option information will be stored
 * @param params additional parameters for the parser
 * @return 0 if everything went fine, NON 0 if an error took place
 */
int cmdline_parser_ext (int argc, char **argv,
  struct gengetopt_args_info *args_info,
  struct cmdline_parser_params *params);

/**
 * Save the contents of the option struct into an already open FILE stream.
 * @param outfile the stream where to dump options
 * @param args_info the option struct to dump
 * @return 0 if everything went fine, NON 0 if an error took place
 */
int cmdline_parser_dump(FILE *outfile,
  struct gengetopt_args_info *args_info);

/**
 * Save the contents of the option struct into a (text) file.
 * This file can be read by the config file parser (if generated by gengetopt)
 * @param filename the file where to save
 * @param args_info the option struct to save
 * @return 0 if everything went fine, NON 0 if an error took place
 */
int cmdline_parser_file_save(const char *filename,
  struct gengetopt_args_info *args_info);

/**
 * Print the help
 */
void cmdline_parser_print_help(void);
/**
 * Print the version
 */
void cmdline_parser_print_version(void);

/**
 * Initializes all the fields a cmdline_parser_params structure 
 * to their default values
 * @param params the structure to initialize
 */
void cmdline_parser_params_init(struct cmdline_parser_params *params);

/**
 * Allocates dynamically a cmdline_parser_params structure and initializes
 * all its fields to their default values
 * @return the created and initialized cmdline_parser_params structure
 */
struct cmdline_parser_params *cmdline_parser_params_create(void);

/**
 * Initializes the passed gengetopt_args_info structure's fields
 * (also set default values for options that have a default)
 * @param args_info the structure to initialize
 */
void cmdline_parser_init (struct gengetopt_args_info *args_info);
/**
 * Deallocates the string fields of the gengetopt_args_info structure
 * (but does not deallocate the structure itself)
 * @param args_info the structure to deallocate
 */
void cmdline_parser_free (struct gengetopt_args_info *args_info);

/**
 * Checks that all the required options were specified
 * @param args_info the structure to check
 * @param prog_name the name of the program that will be used to print
 *   possible errors
 * @return
 */
int cmdline_parser_required (struct gengetopt_args_info *args_info,
  const char *prog_name);

extern const char *cmdline_parser_normm_values[];  /**< @brief Possible values for normm. */


#ifdef __cplusplus
}
#endif /* __cplusplus */
#endif /* CLUSTERDET_CMDLINE_H */