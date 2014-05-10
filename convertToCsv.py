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

# CSV info
HEADERS = [ 'page_no', 'obj_no', 'x0', 'y0', 'x1', 'y1', 'text' ]
PAGES_TO_PARSE = ( 0, 1 )

# Create directory for each issuer in pynha_csv
create_issuer_subdirs( main_dir = 'csv_raw', debug_print = False )
create_issuer_subdirs( main_dir = 'csv_firstpage', debug_print = False )

## NUCLEAR OPTION TO DELETE ALL .CSV FILES IN in CSV_RAW. DO NOT USE ##
## delete_log_files( pattern_str = '.csv', default_start_walk = CSVDIR_RAW )

BIGSIX = [ 'rbc', 'rbc_dominion', 'bmo', 'cibc', 'desjardins', 'national_bank', \
			'national_bank_financial', 'scotia_bank', 'td_bank', 'td_securities' ]

# Delete csv files that failed to parse in ISSUER_DIRS
ISSUER_DIRS = list( gen_issuer_names( skip_list = None ) )

# Delete specific csv files if they failed to parse
##ISSUER_DIRS = [ 'desjardins', 'home_trust', 'national_bank', 'scotia_bank' ]
##delete_csv_from_loggers( issuers_list = ISSUER_DIRS, logging_folder = 'logging_ppl_amount' )

if __name__ == '__main__':
    chdir( PDFDIR )
    failed_files = []
    args = dict( pdf_dir = PDFDIR, csv_dir = CSVDIR_RAW, keep_issuers = ISSUER_DIRS )
    for csv_file, pdf_file in gen_pdf_to_csv( **args ):
        print csv_file, pdf_file
        try:
			writecsv_to_path( csv_file, pdf_file, HEADERS, PAGES_TO_PARSE )
		# TO DO: Replace except Exception hack
        except Exception, err:
			print '\tProblem with file: %s' % ( csv_file )
			failed_files.append( csv_file )
        print 'in directory:' , getcwd()
    print failed_files

