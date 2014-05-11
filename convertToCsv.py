# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 08:34:30 2013

@author: Vathy M. Kamulete
"""

import ioFunc
import recordLoggerId
from ioFunc import create_issuer_subdirs, writecsv_to_path, \
                gen_issuer_names, gen_pdf_to_csv
from os import chdir, getcwd
from os.path import dirname, abspath, join, basename
from recordLoggerId import delete_csv_from_loggers, delete_log_files

# Set global directories
MAINDIR = dirname( dirname( abspath( __file__ ) ) )
HOMEDIR = join( MAINDIR, 'pynha_csv' )
ioFunc.HOMEDIR, recordLoggerId.HOMEDIR = HOMEDIR, HOMEDIR
PDFDIR = join( MAINDIR, 'pynha_scraper', 'pdf_downloaded' )
CSVDIR_RAW = join( HOMEDIR, 'csv_raw' )
CSVDIR_FIRSTPAGE = join( HOMEDIR, 'csv_firstpage' )

# Create directory for each issuer in pynha_csv
create_issuer_subdirs( main_dir = 'csv_raw', debug_print = False )
create_issuer_subdirs( main_dir = 'csv_firstpage', debug_print = False )

## NUCLEAR OPTION TO DELETE ALL .CSV FILES IN in CSV_RAW. DO NOT USE ##
# delete_log_files( pattern_str = '.csv', default_start_walk = CSVDIR_RAW )
# delete_log_files( pattern_str = '.csv', default_start_walk = CSVDIR_FIRSTPAGE )

BIGSIX = [ 'rbc', 'rbc_dominion', 'bmo', 'cibc', 'desjardins', 'national_bank', \
			'national_bank_financial', 'scotia_bank', 'td_bank', 'td_securities' ]

# Delete csv files that failed to parse in ISSUER_DIRS
ISSUER_DIRS = list( gen_issuer_names( skip_list = None ) )

# Delete specific csv files if they failed to parse
##ISSUER_DIRS = [ 'desjardins', 'home_trust', 'national_bank', 'scotia_bank' ]
##delete_csv_from_loggers( issuers_list = ISSUER_DIRS, logging_folder = 'logging_ppl_amount' )

# CSV info
PAGES_TO_PARSE_FIRSTPAGE = ( 0, 1, 2, 3 )
PAGES_TO_PARSE_RAW = ( 5, 6, 7, 8 )

def pdf_to_csv( pdf_dir = PDFDIR, \
                csv_dir = CSVDIR_FIRSTPAGE, \
                keep_issuers = ISSUER_DIRS, \
                pages_to_parse = PAGES_TO_PARSE_FIRSTPAGE ):
    '''
    Convert pdf files in pdf_dir to csv for the pages in pages_to_parse.
    Converted csv files are saved in csv_dir.
    Convert only files belonging to issuers in keep_issuers.
    '''
    HEADERS = [ 'page_no', 'obj_no', 'x0', 'y0', 'x1', 'y1', 'text' ]
    chdir( pdf_dir )
    failed_files = []
    args = dict( pdf_dir = pdf_dir, csv_dir = csv_dir, keep_issuers = keep_issuers )
    for csv_file, pdf_file in gen_pdf_to_csv( **args ):
        print csv_file, pdf_file
        try:
            writecsv_to_path( csv_file, pdf_file, HEADERS, pages_to_parse )
        except Exception, err:
            print '\tProblem with file: %s' % ( csv_file )
            failed_files.append( csv_file )
        print 'in directory:' , getcwd( )
    print failed_files
    return failed_files

if __name__ == '__main__':
    ######### CSVDIR_FIRSTPAGE #########
    pdf_to_csv( pdf_dir = PDFDIR, csv_dir = CSVDIR_FIRSTPAGE, \
                keep_issuers = ISSUER_DIRS, \
                pages_to_parse = PAGES_TO_PARSE_FIRSTPAGE )
    ######### CSVDIR_RAW #########
    pdf_to_csv( pdf_dir = PDFDIR, csv_dir = CSVDIR_RAW, \
            keep_issuers = ISSUER_DIRS, \
            pages_to_parse = PAGES_TO_PARSE_RAW )