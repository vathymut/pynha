# -*- coding: utf-8 -*-
"""
@author: Vathy
"""

from __future__ import division
from ioFunc import gen_issuer_names, create_issuer_dir, safe_delete, create_dir
from contextlib import contextmanager
from os import walk, remove, getcwd, chdir
from os.path import dirname, abspath, join, exists
import csv

# Declare functions to import
__all__ = [ 'write_successes_to_csv', 'write_summ_loggers_to_csv', \
            'log_exceptions', 'delete_log_files', 'create_log_folders', \
            'delete_csv_from_loggers', 'get_stats_from_loggers' ]

def write_successes_to_log( dir_to_log, content, logging_dir = 'logging_rates' ):
    """
    Write successes to log 'success.txt'.
    dir_to_log is the issuer for which the information belongs.
    content is the info to write to csv.
    """
    filename = join( HOMEDIR, logging_dir, dir_to_log, 'success.txt' )
    with open( filename, 'a+' ) as f:
        f.write( content + '\n' )

def write_failures_to_log( dir_to_log, content, logging_dir = 'logging_rates' ):
    """
    Write failures to log 'failure.txt'.
    dir_to_log is the issuer for which the information belongs.
    content is the info to write to csv.
    """
    filename_fullpath = join( HOMEDIR, logging_dir, dir_to_log, 'failure.txt' )
    with open( filename_fullpath, 'a+' ) as f:
        f.write( content + '\n' )

def write_successes_to_csv(  dir_to_log, content, result_type = 'rates' ):
    """
    Write successes to csv.
    result_type is the type of the info: rates, dates, no. of mortgages, etc
    dir_to_log is the issuer for which the information belongs.
    content is the info to write to csv.
    """
    filename = result_type + '.csv'
    filename_fullpath = join( HOMEDIR, result_type, dir_to_log, filename )
    file_exists = exists( filename_fullpath )
    with open( filename_fullpath, 'ab+' ) as f:
        f_csv = csv.writer( f )
        if not file_exists:
            # Write the column headers.
            # content must be a namedtuple with attributes _fields.
            f_csv.writerow( content._fields )
        f_csv.writerow( content )

def write_summary_logs( summ_list, filepath ):
    """
    Write summary logs to csv file.
    """
    COL_FIELDS = [ 'issuer', 'no_failed', 'no_succeeded', 'success_rate' ]
    create_dir( dirname( filepath ) )
    with open( filepath, 'wb' ) as f:
        f_csv = csv.writer( f )
        f_csv.writerow( COL_FIELDS )
        for row in summ_list:
            f_csv.writerow( row )

def write_summ_loggers_to_csv( summ_list, result_type = 'rates', summ_dir = 'summ_loggers' ):
    """
    Write summary logs summ_list to csv file
    result_type in the folder summ_dir.
    """
    no_issuers = len( summ_list )
    overwrite_log = no_issuers == 63
    if not overwrite_log:
        print 'Processed %s issuer(s) -- Not overwriting log folder' % ( no_issuers )
        return
    filename = 'summ_' + result_type + '.csv'
    filename_fullpath = join( HOMEDIR, summ_dir, filename )
    print 'Overwriting log folder'
    write_summary_logs( summ_list = summ_list, filepath = filename_fullpath )

@contextmanager
def log_exceptions( dir_to_log, content, logging_dir, test_run = True ):
    '''
    Log exceptions when trying to extract .csv info.
    '''
    try:
        yield
        if not test_run: # Log success
            write_successes_to_log( dir_to_log, content, logging_dir =  logging_dir )
    except ( ValueError, TypeError ) as err:
        print '\t%s: %s\n' % ( type(err), err.message )
        write_failures_to_log( dir_to_log, content, logging_dir = logging_dir )

def delete_log_files( pattern_str, default_start_walk = 'logging_rates' ):
    '''
    Delete files if the pattern pattern_str matches the filename.
    '''
    args = default_start_walk.split()
    start_dir = join( HOMEDIR, *args )
    for dirpath, _, filenames in walk( start_dir ):
        for f in filenames:
            filepath = join( dirpath, f)
            if pattern_str in filepath:
                print 'Logger deleted: %s' % ( filepath )
                remove( filepath )

def create_log_folders( results_folder = 'rates' , \
                        logging_dir = None, \
                        debug_print = False ):
    """
    Create folders to log files that failed to parse.
    """
    if logging_dir is None:
        logging_dir = 'logging_' + results_folder
    for issuer in gen_issuer_names( ):
        create_issuer_dir( issuer, prefix_path = logging_dir, debug_print = debug_print )
        create_issuer_dir( issuer, prefix_path = results_folder, debug_print = debug_print )

def gen_loggers_path( keep_list = None, logging_folder = 'logging_rates' ):
    """
    Generate path to the logging directories in logging_folder.
    Get all issuers' path if keep_list is None.
    Otherwise get only issuers' path in keep_list.
    """
    for issuer in gen_issuer_names():
        if keep_list and issuer not in keep_list:
            continue
        logpath = join( HOMEDIR, logging_folder, issuer )
        yield logpath, issuer

def gen_csvfailed_path( ):
    """
    Generate filepaths to csv files in failure.txt
    that failed to parse.
    """
    csvpaths = open( 'failure.txt' , 'r' ).readlines()
    csvpaths = [ f.replace( '\n', '' ) for f in csvpaths ]
    for csvpath in csvpaths:
        yield csvpath

def delete_csv_from_loggers( issuers_list, logging_folder = 'logging_rates' ):
    """
    Delete csv files in folder csv_raw for issuer in issuers_list
    if the file is in the failure log.
    """
    CURRDIR = getcwd( )
    DIR_CSV_RAW = join( HOMEDIR, 'csv_raw' )
    try:
        for logpath, issuer in gen_loggers_path( issuers_list, logging_folder ):
            chdir( logpath )
            if not exists( 'failure.txt' ):
                continue
            for csvpath in gen_csvfailed_path( ):
                csv_fullpath = join( DIR_CSV_RAW, issuer, csvpath )
                safe_delete( csv_fullpath )
    finally:
        chdir( CURRDIR )
        print 'Done'

def count_lines( fname ):
    """
    Get a line count. If file doesn't exist, return 0.
    From StackOverflow:
    http://stackoverflow.com/q/845058/1965432
    """
    if not exists( fname ):
        return 0
    with open( fname ) as f:
        for i, l in enumerate( f ):
            pass
        return i + 1

def summ_issuer_logs():
    """
    Return summary stats for issuer about the number of files
    in failure.txt and success.txt. Function assumes that
    current directory is the logging directory.
    """
    success_count = count_lines( 'success.txt' )
    failure_count = count_lines( 'failure.txt' )
    try:
        success_rate = success_count/( success_count + failure_count )
    except  ( ZeroDivisionError, ) as err:
        success_rate = 'TODO'
    return failure_count, success_count, success_rate

def get_stats_from_loggers( issuers_list, logging_folder = 'logging_rates' ):
    """
    Call summ_issuer_logs for each issuer in issuers_list
    and returns stats from the logging_folder.
    """
    RESULTS_LIST = list( )
    for logpath, issuer in gen_loggers_path( issuers_list, logging_folder ):
        chdir( logpath )
        failure_count, success_count, success_rate = summ_issuer_logs( )
        issuer_infolist = [ issuer, failure_count, success_count, success_rate ]
        RESULTS_LIST.append( issuer_infolist )
    return RESULTS_LIST

if __name__ == '__main__' :
    # Include tests here if needed
    print 'Leave blank for now'

