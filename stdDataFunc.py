# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 08:34:30 2013

@author: Vathy M. Kamulete
"""
from collections import namedtuple
import re
import csv
from os.path import basename
from functools import partial, wraps, update_wrapper
from itertools import chain
from time import sleep

def gen_namedcsvrow( filename, headers ):
	'''
	Generate csv rows as namedtuples for filename.
	Each row gets its name from headers.
	'''
	# Create container for row
	Row = namedtuple( 'csvrow', headers )
	with open( filename, 'r' ) as infile:
		reader = csv.reader( infile )
		# Skip first row
		next( reader )
		for line in reader:
			row = Row( *line )
			yield row

def gen_id_csvrows( filename, headers, skip_rows_no = 0, stop_row_no = 100 ):
	'''
	For each filename, skip the first skip_rows_no (int) rows.
	Stop at the stop_row_no (int) th rows.
	'''
	for idx, row in enumerate( gen_namedcsvrow( filename, headers ) ):
		if idx < skip_rows_no:
			continue
		if idx > stop_row_no:
			break
		yield row

def get_csvrows( filename, headers, skip_rows_no = 0, stop_row_no = 100 ):
    '''
    Get rows list from the generator gen_id_csvrows.
    '''
    kwargs = dict( filename = filename, headers = headers, \
                    skip_rows_no = skip_rows_no, stop_row_no = stop_row_no )
    return list( gen_id_csvrows( **kwargs ) )

def extract_text( rows ):
	'''
	Extract text from rows. Return text in a single line.
	'''
	rows_list = [ row.text for row in rows ]
	rows_lines = ' '.join( rows_list )
	return rows_lines

def remove_false_matches( rows_lines, delete_regex = None ):
    '''
    Delete all text in rows_lines matching compiled regex delete_regex.
    '''
    if delete_regex is None:
        return rows_lines
    return delete_regex.sub( '', rows_lines )

def set_text_beginning( rows_lines, start_regex = None ):
    '''
    Delete text in rows_lines preceding the compiled regex start_regex.
    '''
    try:
        m = start_regex.search( rows_lines )
        return rows_lines[ m.start(): ]
    except ( AttributeError, ) as err:
        return rows_lines

def set_text_ending( rows_lines, end_regex = None ):
    '''
    Delete text in rows_lines after the compiled regex end_regex.
    '''
    try:
        m = end_regex.search( rows_lines )
        return rows_lines[ :m.start() ]
    except ( AttributeError, ) as err:
        return rows_lines

def trim_text( rows_lines, start_regex = None, end_regex = None ):
    '''
    trim text in rows_lines by deleting both everything before
    the regex start_regex and everything after the regex end_regex.
    '''
    rows_lines = set_text_beginning( rows_lines, start_regex = start_regex )
    rows_lines = set_text_ending( rows_lines, end_regex = end_regex )
    return rows_lines

def extract_pattern( rows_lines, patterns ):
    '''
	Extract the items in rows_lines matching the regex patterns.
    patterns is the compiled regex.
    '''
    result_list = patterns.findall( rows_lines )
    if not result_list:
		print '\tText: \n%s \n' % ( rows_lines )
		raise ValueError( "No text macthes regex." )
    return result_list

def get_pool_info( rows_to_test, patterns, \
                delete_regex = None, \
                start_regex = None, \
                end_regex = None ):
    '''
	Return text in rows_to_test matching the regex in patterns.
	If given, text preceding delete_regex is removed before matching.
    If given, text before start_regex is removed before matching.
    If given, text after end_regex is removed before matching.
    All regex must be compiled.
	'''
    rows_lines = extract_text( rows_to_test )
    rows_lines = remove_false_matches( rows_lines, delete_regex = delete_regex )
    rows_lines = trim_text( rows_lines, start_regex = start_regex, end_regex = end_regex )
    result_list = extract_pattern( rows_lines, patterns )
    return result_list

def get_x0_diff( row, ref_x0 ):
    '''
    Return the distance of the row's leftmost position (x0)
    from the reference point ref_x0.
    '''
    x0, ref_x0 = float( row.x0 ), float( ref_x0 )
    return x0 - ref_x0

def get_y0_diff( row, ref_y0 ):
    '''
    Return the distance of the row's uppermost position (y0)
    from the reference point ref_y0.
    '''
    y0, ref_y0 = float( row.y0 ), float( ref_y0 )
    return ref_y0 - y0

def get_score_diff( row, ref_cord ):
	'''
	Wrapper around the get_*_diff functions.
	Return tuple of the results from the latter.
	(ref_cord) is the reference point ( ref_x0, ref_y0 ).
	'''
	x0_diff = get_x0_diff( row, ref_cord[0] )
	y0_diff = get_y0_diff( row, ref_cord[1] )
	return ( x0_diff, y0_diff )

from math import exp
def exp_pct_errors( row, ref_cord ):
	'''
	Return loss function as the square of the percentage difference between row and ref_cord
	(ref_cord) is the reference point ( ref_x0, ref_y0 ).
	'''
	x0, ref_x0 = float( row.x0 ), float( ref_cord[0] )
	y0, ref_y0 = float( row.y0 ), float( ref_cord[1] )
	x0_pct_diff = abs( x0 - ref_x0 )/ref_x0
	y0_pct_diff = abs( y0 - ref_y0 )/ref_y0
	# Exponential errors
	errors_penalty = exp( x0_pct_diff*1. + y0_pct_diff*4. )
	return errors_penalty

def in_range( diff_tuple, cutoff_tuple, absdist_tuple = (-25.0, -25.0) ):
    '''
	Return True if diff_tuple (x0_diff, y0_diff) is within an acceptable range.
	cutoff_tuple (x0_max, y0_max) is the relative max acceptable distance of diff_tuple.
    absdist_tuple (x0_floor, y0_floor) is the absoulte max distance of diff_tuple.
    x0_floor and y0_floor filters for for large deviation:
        either too much to the left or above the reference coordinates.
	'''
    x0_test = float( abs( diff_tuple[0] ) ) < float( cutoff_tuple[0] )  # leftmost: points diff
    y0_test = float( abs( diff_tuple[1] ) ) < float( cutoff_tuple[1] )  # topmost: points diff
    x0_ngtv_test = float( diff_tuple[0] ) > float( absdist_tuple[0] )   # Checks for large negative x0.
    y0_ngtv_test = float( diff_tuple[1] ) > float( absdist_tuple[1] )   # Checks for large negative y0.
    return all( [ x0_test, y0_test, y0_ngtv_test, x0_ngtv_test ] )

def filter_rows( rows_list, ref_cord, cutoff_tuple, absdist_tuple = (-25.0, -25.0) ):
    '''
	Filter rows_list to keep rows within acceptable range of the
	ref_cord (the reference point).
    '''
    get_filter_diff = partial( get_score_diff, ref_cord = ref_cord )
    kwargs = dict( cutoff_tuple = cutoff_tuple, absdist_tuple = absdist_tuple )
    in_range_custom = partial( in_range, **kwargs )
    is_diff_range = lambda row: in_range_custom( get_filter_diff( row ) )
    l = filter( is_diff_range, rows_list )
    if not l:
		diffs = map( get_filter_diff, rows_list )
		min_diff = min( diffs )
		print 'Minimum distance:', min_diff
		print 'Reference coordinates:', ref_cord
		raise ValueError( "Filtering returns empty list." )
    return l

def sort_rows( filtered_rows, ref_cord = None, use_loss_function = False ):
	'''
	Sort rows in filtered_rows according to attributes ( x0, y0 ).
	ref_cord is the tuple ( x0, y0 ) of the reference point.
	'''
	if use_loss_function and ref_cord is not None:
		comp_func = partial( exp_pct_errors, ref_cord = ref_cord )
		filtered_rows.sort( key = comp_func )
		return filtered_rows
	filtered_rows.sort( key = lambda row: ( float( row.page_no ), -float( row.y0 ), float( row.x0 ) ) )
	return filtered_rows

def join_namedtuples( namedtuples_list, idname = 'idPool' ):
	'''
	Return a namedtuple joined from namedtuples_list.
	*namedtuples becomes a list. idname is the name of the final namedtuple.
	'''
	names = [ field for tup in namedtuples_list for field in tup._fields ]
	info = [ info for tup in namedtuples_list for info in tup ]
	named_tuple = namedtuple( idname, names )
	return named_tuple( *info )

# A LITTLE BIT OF PYTHON MAGIC -- Decorator :)
def convert_to_namedtuple( idname, colnames ):
    '''
	Decorator to change list to namedtuple. See StackOverflow:
	http://stackoverflow.com/q/12161649/1965432
	Func could be:
		get_rate, get_mtgtotno, get_poolno
		get_date_issue, get_date_due, get_date_interest
    '''
    def _wrapper( func ):
        @wraps( func )
        def __changefunc( *args, **kwargs ):
            info = func( *args, **kwargs )
            idTuple = namedtuple( idname, colnames )
            try:
                info_named = idTuple( *info )
            except ( Exception, ) as err:
                print 'Info:', info
                raise err
            return info_named
        return __changefunc
    return _wrapper

@convert_to_namedtuple( 'idPoolNo', 'poolno' )
def get_poolno( csv_filename ):
	'''
	Return pool no (as a list).
	'''
	filename = basename( csv_filename )
	poolno = filename.split('-')[:1]
	return poolno

def partial_with_wrapper( func, **kwargs ):
    '''
    Return partial function func with the updated wrapper.
    '''
    func_partial = partial( func, **kwargs )
    update_wrapper( func_partial, func )
    return func_partial

# DEBUG FUNCTION BY REMOVING SPURRIOUS BRANCHES
# Create closure function
def customize_func( get_data_func, cutoff_tuple = None ):
    '''
	Closure to return customized function to extract data.
	based on pixel positions of pdf files.
	'''
    if cutoff_tuple is not None:
        custom_get_data_func = partial_with_wrapper( get_data_func, cutoff_tuple = cutoff_tuple )
    else:
        custom_get_data_func = get_data_func
    def get_info( rows_list, csv_filename, tuple_coord = None, \
                debug_print = True, absdist_tuple = (-25.0, -25.0) ):
        '''
        Return namedtuple of the pool info from rows_list in csv_filename.
        The poolno is in the filename.
        other_info could be:
            rates, dates issued, dates due, no. of mortgages, etc
        if tuple_coord is None, the function looks for an anchor to get
        the reference coordinates.
        '''
        poolno = get_poolno( csv_filename )
        if debug_print:
            print poolno
        kwargs = dict( ref_cord = tuple_coord, absdist_tuple = absdist_tuple )
        if cutoff_tuple is not None and absdist_tuple is not None:
            other_info = custom_get_data_func( rows_list, **kwargs )
        else:
            other_info = custom_get_data_func( rows_list )
        results = [ poolno, other_info ]
        pl_info = join_namedtuples( results, idname = 'idPool' )
        if debug_print:
			print pl_info
        return pl_info
    return get_info