# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 08:34:30 2013

@author: Vathy M. Kamulete
"""
from os import getcwd, listdir, chdir, mkdir, makedirs, remove
from os.path import splitext, exists, dirname, basename, join, isdir, abspath
from glob import glob
import contextlib
import csv
from time import sleep

def safe_delete( path ):
    '''
    Remove a file. Return True if it succeeds. False, otherwise.
    Prints to screen if file does not exist.
    '''
    try:
        remove( path )
        print 'Deleted: %s' %( path )
        return True
    except IOError, OSError:
        print 'File not found: %s' % ( path )
        return False

def create_dir( d ):
	'''
	Create directory d if it does not exist already.
	Taken from StackOverflow:
	http://stackoverflow.com/q/273192/1965432
	'''
	if not exists( d ):
		makedirs( d )
		return True
	else:
		return False

@contextlib.contextmanager
def goto_pdf_dir( save_dir, home_dir, debug_print = True ):
	'''
	Go to directory save_dir. Do something.
	Go back to directory home_dir when done.
	'''
	try:
		chdir( save_dir )
		if debug_print:
			print '...inside: %s' %( getcwd() )
		yield
	finally:
		chdir( home_dir )
		if debug_print:
			print '...back: %s' %( getcwd() )

def create_issuer_dir( filename, prefix_path = 'pdf_downloaded' , debug_print = True ):
	'''
	Create directory for issuer.
	Return the existing or newly created directory for the issuer.
	'''
	issuer, _ = splitext( filename )
	new_issuer_dir = join( prefix_path, issuer )
	is_created = create_dir( new_issuer_dir )
	if debug_print:
		if is_created:
			print "Created directory for %s: %s \n" % (issuer, is_created)
		else:
			print "Directory for %s already exists \n" % (issuer)
	return new_issuer_dir

def gen_issuer_names( skip_list = None ):
    '''
	Generate issuers names. When done, return to current directory.
	If the issuer's name is in skip_list, skip.
	'''
    CURRDIR = getcwd( )
    try:
        chdir( HOMEDIR )
        issuers_filenames = glob( '*.txt' )
        for filename in issuers_filenames:
			issuer, _ = splitext( filename )
			if skip_list is not None and issuer in skip_list:
				continue
			yield issuer
    finally:
		chdir( CURRDIR )

def create_issuer_subdirs( main_dir = 'csv_raw' , debug_print = False ):
	'''
	Create subfolder for each issuer in the directory main_dir.
	'''
	for issuer in gen_issuer_names( ):
		create_issuer_dir( issuer, prefix_path = main_dir, debug_print = debug_print )

def navigate_dirs( home_dir ):
	'''
	Get all subdfolders in the directory home_dir.
	Typically, home_dir contains dir of each issuer.
	'''
	chdir( home_dir )
	for dirname in listdir( getcwd() ):
		if isdir( dirname ):
			yield dirname

def check_if_dir_to_visit( dir, dirs_to_visit  ):
	'''
	Check if the dir is in tuples of dirs_to_visit
	'''
	short_dirname = basename( dir )
	if short_dirname in dirs_to_visit:
		return True
	return False

def check_if_csvexists( csv_filename, in_dir, debug_print = True ):
	'''
	Check if csv_filename already exists.
	in_dir is the directory in which to check.
	'''
	if csv_filename in listdir( in_dir ):
		if debug_print:
			print 'Skipping %s' % ( csv_filename )
		return True
	if debug_print:
		print "%s not in %s" % ( csv_filename, in_dir )
	return False

def give_csvname( pdf_filename ):
	'''
	Change extension of pdf_filename to csv.
	'''
	fileno, _ = splitext( pdf_filename )
	csv_filename = fileno + '.csv'
	return csv_filename

def get_dir_and_fileinfo( from_dir, to_dir, first_ten = False ):
    '''
	Return file no., filename and directory in each subdirectory of to_dir.
	Function assumes that from_dir and to_dir have the same subdirectories.
	first_ten takes the first 10 files from each issuer.
    '''
    for dirname in navigate_dirs( home_dir = from_dir ):
		in_dir = join( HOMEDIR, to_dir, dirname )
		with goto_pdf_dir( save_dir = dirname, home_dir = from_dir, debug_print = first_ten ):
			if first_ten:
				print '\nFirst 10 files in directory:'
			for file_no, filename in enumerate( listdir( getcwd() ) ):
				if first_ten and file_no > 9:
					continue
				yield file_no, filename, in_dir

def gen_pdf_to_csv( pdf_dir, csv_dir, keep_issuers ):
    '''
    Generates from the folder pdf_dir the pdf files to be converted
    to csv files and saved in the folder csv_dir.
    Only process files belonging to issuers in keep_issuers.
    '''
    args = dict( from_dir = pdf_dir, to_dir = csv_dir )
    for _, pdf_file, csv_dir in get_dir_and_fileinfo( **args ):
        if not check_if_dir_to_visit( csv_dir, dirs_to_visit = keep_issuers ):
            continue
        csv_file = give_csvname( pdf_file )
        if check_if_csvexists( csv_file, in_dir = csv_dir ):
            continue
        csv_file = join( csv_dir, csv_file )
        yield csv_file, pdf_file

from pdfFunc import gen_rows_frompath
def writecsv_to_path( to_path, from_path, headers, pages_to_parse  ):
	'''
	Write the contents of pages in pages_to_parse from from_path to to_path.
	The content is saved in csv format.
	'''
	with open( to_path, 'wb' ) as f:
		f_csv = csv.writer( f )
		# Write first row (columns)
		f_csv.writerow( headers )
		for csv_row_list in gen_rows_frompath( from_path, pages_to_parse ):
			f_csv.writerow( csv_row_list )

def read_as_set( dir_to_log, filename = 'success.txt', logging_dir = 'logging_rates' ):
    '''
    Read contents of file into a set.
    '''
    filepath = join( HOMEDIR, logging_dir, dir_to_log, filename )
    try:
        with open( filepath, 'r' ) as f:
            lines = f.readlines( )
            lines = [ l.strip() for l in lines ]
            return set( lines )
    except IOError as err:
        print '\t\t Logger not created as of yet.'
        return set()

def write_set_to_file( filename, lines_as_set ):
    '''
    Write the set lines_as_set to filename.
    '''
    with open( filename, 'w' ) as f:
        for elem in lines_as_set:
            f.write( elem + '\n' )

def skip_dir( to_dir, from_dir = 'csv_raw', keep_list = None ):
    '''
    Visit all directories in from_dir if keep_list is None.
    Otherwise, only visit dir in keep_list.
    Returns file no., filename and issuer to be processed in to_dir.
	'''
    csvdir = join( HOMEDIR, from_dir )
    for fileno, filename, clean_dir in get_dir_and_fileinfo( from_dir = csvdir, to_dir = to_dir, first_ten = False ):
		issuer = basename( clean_dir )
		if keep_list is None:
			yield fileno, filename, issuer
		elif issuer in keep_list:
			yield fileno, filename, issuer

def skip_files( skip_dir_gen, logging_dir = 'logging_rates' ):
    '''
    Return file no., filename and  issuer of csv files not processed.
   	Skip the csv files that were successfully processed.
	skip_dir_gen is the generator from calling skip_dir.
	'''
    logging_dir = join( HOMEDIR, logging_dir )
	# Initiate set of previously succesfully processed files
    logged_successes = set( [] )
    for file_no, csv_filename, issuer in skip_dir_gen:
		if file_no == 0:
			logged_successes = read_as_set( dir_to_log = issuer, \
											filename = 'success.txt', \
											logging_dir = logging_dir )
		if logged_successes and csv_filename in logged_successes:
			print '%s was already processed: \tcontinue' % ( csv_filename )
			continue
		yield file_no, csv_filename, issuer

def get_files_to_process( to_dir, \
                        keep_list = None, \
                        logging_dir = 'logging_rates', \
                        from_dir = 'csv_raw' ):
    '''
	Returns the csv_filenames in from_dir to be processed.
	Wrapper around the function skip_dir and skip_files.
	'''
    logging_dir = join( HOMEDIR, logging_dir )
    csvdir = join( HOMEDIR, from_dir )
    skip_dir_gen = skip_dir( to_dir = to_dir, from_dir = csvdir, keep_list = keep_list )
    skip_files_gen = skip_files( skip_dir_gen, logging_dir = logging_dir )
    for file_no, csv_filename, issuer in skip_files_gen:
		yield file_no, csv_filename, issuer

if __name__ == '__main__' :
	# Include tests here if needed
    print 'Leave blank for now'
    set_globals_dir( )
    print 'The home directory in this computer is:', HOMEDIR
    print 'The project directory in this computer is:', PYNHADIR
    chdir( PYNHADIR )