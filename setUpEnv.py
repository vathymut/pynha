# -*- coding: utf-8 -*-
"""
@author: Vathy
"""
from time import sleep
from contextlib import contextmanager
from ioFunc import gen_issuer_names, get_files_to_process
from os import chdir, getcwd
from os.path import join, dirname, abspath
from stdDataFunc import get_csvrows, partial_with_wrapper
from recordLoggerId import log_exceptions, write_successes_to_csv, create_log_folders, \
                        get_stats_from_loggers, write_summ_loggers_to_csv, delete_log_files

def gen_cutoff( func_custom, cutoff_list = None ):
    """
    Yields function func_custom with default argument
    cutoff_tuple from elements in cutoff_list.
    func_custom can be:
        custom_rate_p1, custom_mtgtotno, custom_date_issue
        custom_date_due, custom_date_interest, etc
    """
    if cutoff_list is not None:
        for cutoff in cutoff_list:
            func_with_cutoff = func_custom( cutoff_tuple = cutoff )
            yield func_with_cutoff
    else:
        func_with_cutoff = partial_with_wrapper( func_custom, cutoff_list = cutoff_list )
        yield func_with_cutoff

def gen_refcoord( func_with_cutoff, refcoord_list = None ):
    """
    Yields function func_with_cutoff with default argument
    tuple_coord from elements in refcoord_list
    func_with_cutoff might come from gen_cutoff.
    """
    if refcoord_list is not None:
        for refcoord in refcoord_list:
            func_with_ref = partial_with_wrapper( func_with_cutoff, tuple_coord = refcoord )
            yield func_with_ref
    else:
        func_with_ref = partial_with_wrapper( func_with_cutoff, tuple_coord = refcoord_list )
        yield func_with_ref

def gen_refcoord_and_cutoff( func_custom, cutoff_list = None, refcoord_list = None ):
    """
	Customize the function func_custom to get the data.
	refcoord_list are the (x0, y0) reference coordinates to find the info on the page.
	cutoff_list are the maximum (x0, y0) differences to the reference coordinate.
    """
    for f_cut in gen_cutoff( func_custom, cutoff_list):
        for f_ref in gen_refcoord( f_cut, refcoord_list ):
            yield f_ref

def gen_func_with_args( gen_func, partial_get_files, logging_dir ):
	"""
	Generates the function arguments to be passed along with the customized function.
	partial_get_files generates the files to be processed.
	gen_func generates the customized functions to be called.
	logging_dir is the directory where outcomes are logged.
	"""
	for func in gen_func:
		delete_log_files( pattern_str = 'failure.txt', default_start_walk = logging_dir )
		for _, csv_filename, issuer in partial_get_files():
			yield csv_filename, issuer, func

def set_gen_extract_data( func_custom, cutoff_list = None, refcoord_list = None ):
    """
    Set appropriate defaults to func_custom.
    Return generator consisting of func_custom with different arguments.
    """
    args_dict = dict( func_custom = func_custom, refcoord_list = refcoord_list, cutoff_list = cutoff_list )
    return gen_refcoord_and_cutoff( **args_dict )

def set_gen_func_with_args( gen_func, logging_dir, gen_get_files ):
    """
    Set appropriate defaults to func_custom.
    Return generator consisting of:
        csv_filename, filename to process
        issuer (self-explanatory)
        func, function to apply to csv file to extract info.
    This wraps set_gen_extract_data and set_get_files together.
    """
    args_dict = dict( gen_func = gen_func, partial_get_files = gen_get_files, logging_dir = logging_dir )
    return gen_func_with_args( **args_dict )

def wrap_set_up_env( func_custom, \
                    cutoff_list = None, \
                    refcoord_list = None, \
                    result_type = 'rates', \
                    logging_dir = 'logging_rates', \
                    keep_list = None, \
                    from_dir = 'csv_raw' ):
    """
    Takes care of overhead in setting up all the relevant functions.
    """
    create_log_folders( results_folder = result_type, logging_dir = logging_dir, debug_print = False )
    # Create log_outcomes
    log_outcomes = partial_with_wrapper( log_exceptions, logging_dir = logging_dir )
    write_info = partial_with_wrapper( write_successes_to_csv, result_type = result_type )
    # Get files to process
    args_dict = dict( to_dir = result_type, from_dir = from_dir, logging_dir = logging_dir, keep_list = keep_list )
    get_files = partial_with_wrapper( get_files_to_process, **args_dict )
    # Customize function to extract data
    args_dict = dict( func_custom = func_custom, refcoord_list = refcoord_list, cutoff_list = cutoff_list )
    gen_extract_data = set_gen_extract_data( **args_dict )
    # Set files to be processed with function
    args_dict = dict( gen_func = gen_extract_data, logging_dir = logging_dir, gen_get_files = get_files )
    set_up_env = set_gen_func_with_args( **args_dict )
    return log_outcomes, write_info, set_up_env

@contextmanager
def handle_newline_error( ):
    """
    Handle exception err with message: 'newline inside string'
    This supposedly catches corrupt Scotia csv files.
    """
    try:
        yield
    except ( Exception, ) as err:
        if 'newline inside string' in err.message:
            print 'Silently passes error: %s' % ( err.message )
        else:
            raise err

def process_csv_files( set_up_env, \
                    log_outcomes, \
                    write_info, \
                    skip_rows_no = 0, \
                    stop_row_no = 120, \
                    result_type = 'rates', \
                    logging_dir = 'logging_rates', \
                    absdist_tuple = None, \
                    test_run = True ):
    """
    Process csv files and return csv files not processed.
    Assumes that wrap_set_up_env( ... ) has alreeady been called.
    Otherwise, log_outcomes, write_info, set_up_env don't exist.
    If test_run, do not write results to file.
    """
    HEADERS_CSV = [ 'page_no', 'obj_no', 'x0', 'y0', 'x1', 'y1', 'text' ]
    for csv_filename, issuer, extract_data in set_up_env:
        kwargs = dict( filename = csv_filename, headers = HEADERS_CSV, skip_rows_no = skip_rows_no, stop_row_no = stop_row_no )
        with handle_newline_error( ):
            rows_list = get_csvrows( **kwargs )
            with log_outcomes( dir_to_log = issuer, content = csv_filename, test_run = test_run ):
                if absdist_tuple is None:
                    pl_info = extract_data( rows_list, csv_filename )
                else:
                    pl_info = extract_data( rows_list, csv_filename, absdist_tuple = absdist_tuple )
                write_info( dir_to_log = issuer, content = pl_info )

# Declare functions to import
__all__ = [ 'wrap_set_up_env', 'process_csv_files' ]

if __name__ == '__main__' :
    from makeInsAmountExposed import get_ins_amounts
    from os import getcwd
    # test wrap_set_up_env
    args_dict = dict( cutoff_list = None, refcoord_list = None, \
                    result_type = 'ins_amounts', logging_dir = 'logging_insnha_inspriv', \
                    func_custom = get_ins_amounts, from_dir = 'csv_raw' )
    log_outcomes, write_info, set_up_env = wrap_set_up_env( **args_dict )
    for csv_filename, issuer, extract_data in set_up_env:
        print 'dir:', getcwd( )
        print 'csv_filename:', csv_filename
        print 'issuer:', issuer
        print 'function name:', extract_data.__name__