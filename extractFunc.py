# -*- coding: utf-8 -*-
"""
Created on 26/04/2014

@author: Vathy M. Kamulete
"""
from stdDataFunc import partial_with_wrapper, filter_rows, \
                        sort_rows, get_pool_info, customize_func
import string
from time import sleep
from setUpEnv import wrap_set_up_env, process_csv_files
from recordLoggerId import get_stats_from_loggers, \
                        write_summ_loggers_to_csv, delete_log_files
from ioFunc import gen_issuer_names

def get_namedtuple( rows_list, sort_func, extract_func, \
                    cutoff_tuple = None, last_idx = 5, \
                    ref_cord = None, absdist_tuple = (-25.0, -25.0) ):
    '''
    sort_func filters the rows in rows_list accordingly.
    extract_func extracts data from the sorted rows in a list.
    last_idx takes the nth element from the resulting list above.
    if ref_cord is None, try to find it.
    Otherwise ref_cord is tuple of (x0, y0) reference coordinates.
    cutoff_tuple is the relative max acceptable distance to ref_cord.
    absdist_tuple is the absoulte max acceptable distance to ref_cord.
    '''
    if cutoff_tuple is not None:
        args_dict = dict( cutoff_tuple = cutoff_tuple, ref_cord = ref_cord, absdist_tuple = absdist_tuple )
        sorted_rows = sort_func( rows_list, **args_dict )
        return extract_func( sorted_rows )[ :last_idx ]
    sorted_rows = sort_func( rows_list )
    return extract_func( sorted_rows )

def find_ref_coord( rows_to_test, refcoord_regex, fp_regex = None ):
    '''
    Find the row in rows_to_test whose text matches the regex refcoord_regex.
    Return the coordinate tuple (x0, y0) of the matching row.
    Also return the index of the matching row.
    If the row matches the regex fp_regex (false positive), discard result.
    '''
    for idx_refcord, row in enumerate( rows_to_test ):
        m = refcoord_regex.search( row.text )
        if fp_regex is not None:
            n = fp_regex.search( row.text )
            if m and not n:
                return ( float( row.x0 ), float( row.y0 ) ), idx_refcord
        elif m and fp_regex is None:
            return ( float( row.x0 ), float( row.y0 ) ), idx_refcord
    raise ValueError( "No reference coordinates found." )

def sort_for_info( rows_list, func_find, cutoff_tuple = None,  \
                ref_cord = None, use_loss_function = False, \
                absdist_tuple = (-25.0, -25.0), \
                idx_offset = 15 ):
    '''
    Return rows for rows_list matching the criteria based on:
        cutoff_tuple, ref_cord and func_sort
    func_find should be a function i.e. find_refrate, find_refdateissue, etc
    '''
    rows_list = sort_rows( rows_list, ref_cord = ref_cord, use_loss_function = use_loss_function )
    if ref_cord is None:
        ref_cord, idx_refcord = func_find( rows_list )
    args_dict = dict( ref_cord = ref_cord, cutoff_tuple = cutoff_tuple, absdist_tuple = absdist_tuple )
    idx_stoprow = idx_refcord + idx_offset
    if cutoff_tuple is not None:
        return filter_rows( rows_list[ :idx_stoprow], **args_dict )
    return rows_list[ idx_refcord : idx_stoprow ]

def set_default_to_sort( refcoord_regex, fp_regex = None, idx_offset = 15 ):
    '''
    Return function to sort rows with the appropriate default arguments.
    refcoord_regex finds the position of the anchor text.
    fp_regex (false positive) discards the result if it matches.
    '''
    args_dict = dict( refcoord_regex = refcoord_regex, fp_regex = fp_regex )
    find_cust = partial_with_wrapper( find_ref_coord, **args_dict )
    args_dict = dict( func_find = find_cust, idx_offset = idx_offset )
    return partial_with_wrapper( sort_for_info, **args_dict )

def is_sorted( rows_list, sort_func, cutoff_tuple = None, \
                ref_cord = None, absdist_tuple = (-25.0, -25.0) ):
    '''
    Returns True if a row in rows_list matches the format specified.
    if ref_cord is None, try to find it first.
    Otherwise ref_cord is tuple of (x0, y0) reference coordinates.
    cutoff_tuple is the relative max acceptable distance to ref_cord.
    absdist_tuple is the absoulte max acceptable distance to ref_cord.
    '''
    args_dict = dict( ref_cord = ref_cord, absdist_tuple = absdist_tuple )
    try:
        if cutoff_tuple is not None and ref_cord is not None:
            sort_func( rows_list, cutoff_tuple, **args_dict )
        else:
            sort_func( rows_list )
        return True
    except ( ValueError, ) as err:
        return False

def count_instances( string_to_test, types = string.digits ):
    '''
    Count the number of types (digits) found in the string string_to_test.
    '''
    string_as_list = list( string_to_test )
    string_list_filtered = filter( lambda x: x in types, string_as_list )
    return len( string_list_filtered )

def count_digits_and_letters( string_to_test, \
                            digits = string.digits, \
                            letters = string.ascii_letters ):
    '''
    Count the number of types (digits) found in the string string_to_test.
    '''
    no_digits = count_instances( string_to_test, types = digits )
    no_letters = count_instances( string_to_test, types = letters )
    return ( no_digits, no_letters )

def validate_amount( result_list, types = string.digits, \
                    min_digits = 6, max_digits = 13 ):
    '''
    Return result_list if it passes format check for dollar amount.
    '''
    no_digits = count_instances( result_list[0], types = types )
    if max_digits > no_digits > min_digits:
        return result_list
    error_print = "The amount is %d digits or less or %d digits or more." % ( min_digits, max_digits )
    raise ValueError( error_print )

def validate_mtgno( result_list, types = string.digits, \
                    min_digits = 1, max_digits = 5 ):
    '''
    Return result_list if it passes format check for mortgage number.
    '''
    no_digits = count_instances( result_list[0], types = types )
    if max_digits >= no_digits >= min_digits:
        return result_list
    error_print = "The number of mortgages is %d digits or less or %d digits or more." % ( min_digits, max_digits )
    raise ValueError( error_print )

def validate_dates( result_list, \
                    min_digits = 4, max_digits = 8, \
                    min_letters = 2 ):
    '''
    Return result_list if it passes format check for dates.
    '''
    digits_and_letters = map( count_digits_and_letters, result_list )
    digits_fmt = [ max_digits > num[0] >= min_digits for num in digits_and_letters ]
    letters_fmt = [ num[1] >= min_letters for num in digits_and_letters ]
    if all( digits_fmt ) and all( letters_fmt ):
        return result_list
    error_print = "The dates do not all pass the format check."
    raise ValueError( error_print )

def validate_rate( result_list, types = string.digits, \
                    min_digits = 1, max_digits = 7 ):
    '''
    Return result_list if it passes format check for dollar amount.
    '''
    no_digits = count_instances( result_list[0], types = types )
    if max_digits > no_digits > min_digits:
        return result_list
    error_print = "The rate is %d digits or less or %d digits or more." % ( min_digits, max_digits )
    raise ValueError( error_print )

def redo_issuer( result_type, keep_list = None, logging_dir = None ):
    '''
    Delete all the previous results for issuers in keep_list.
    If keep_issuers is None, get all issuers.
    '''
    if logging_dir is None:
        logging_dir = 'logging_' + result_type
    if keep_list is None:
        keep_list = gen_issuer_names( skip_list = keep_list )
    for issuer in keep_list:
        issuer_result = ' '.join( [ result_type, issuer ] )
        issuer_logging_dir = ' '.join( [ logging_dir, issuer ] )
        delete_log_files( '.txt', issuer_logging_dir )
        delete_log_files( '.csv', issuer_result )

def extract_info( func_custom, \
                    result_type, \
                    logging_dir, \
                    keep_list = None, \
                    cutoff_list = None, \
                    refcoord_list = None, \
                    skip_rows_no = 0, \
                    stop_row_no = 120, \
                    from_scratch = False, \
                    absdist_tuple = (-25.0, -25.0), \
                    test_run = True, \
                    from_dir = 'csv_raw' ):
    '''
    Extract info from the circulars using the function func_custom.
    func_custom could be:
        custom_rate, custom_date_issue, custom_date_due
    cutoff_tuple and refcoord_list are arguments to func_custom.
    headers, skip_rows and stop_rows are arguments to gen_id_csvrows.
    Save the extracted info to files (loggers and csv) if it succeeds.
    If it fails, it logs the file info to appropriate loggers.
    If from_scratch, delete all the previous results for issuers in keep_list.
    If test_run, do not write results to file.
    from_dir is the folder of csv files where the circulars are.
    '''
    if from_scratch:
        redo_issuer( result_type, keep_list = keep_list, logging_dir = logging_dir )
    args_dict = dict( cutoff_list = cutoff_list, refcoord_list = refcoord_list, \
                    result_type = result_type, logging_dir = logging_dir, \
                    keep_list = keep_list, func_custom = func_custom, from_dir = from_dir )
    log_outcomes, write_info, set_up_env = wrap_set_up_env( **args_dict )
    # Process files
    args_dict = dict( set_up_env = set_up_env, log_outcomes = log_outcomes, \
                    write_info = write_info, skip_rows_no = skip_rows_no, \
                    stop_row_no = stop_row_no, result_type = result_type, \
                    logging_dir = logging_dir, absdist_tuple = absdist_tuple, \
                    test_run = test_run )
    ftl_files = process_csv_files( **args_dict )
    # Get stats
    stats = get_stats_from_loggers( issuers_list = keep_list, logging_folder = logging_dir )
    print '\n\t\t\tPrinting stats:\n\n', stats
    write_summ_loggers_to_csv( stats, result_type = result_type )
    print '\n\t\t\tDone.'
    return ftl_files

def set_extract_default( func_custom, result_type, \
                    logging_dir = None, cutoff_list = None, \
                    absdist_tuple = (-25.0, -25.0), from_dir = 'csv_raw' ):
    '''
    Set default to extract_info
    '''
    if logging_dir is None:
        logging_dir = 'logging_' + result_type
    if absdist_tuple is not None:
        args_dict = dict( func_custom = func_custom, cutoff_list = cutoff_list, \
                        result_type = result_type, logging_dir = logging_dir, \
                        absdist_tuple = absdist_tuple, from_dir = from_dir )
    else:
        args_dict = dict( func_custom = func_custom, cutoff_list = cutoff_list, \
                        result_type = result_type, logging_dir = logging_dir, \
                        from_dir = from_dir )
    return partial_with_wrapper( extract_info, **args_dict )

def create_default_dictargs( issuer = 'alberta_treasury' ):
    '''
    Set default function arguments for issuer in dict.
    '''
    return issuer, dict( keep_list = [ issuer ], from_scratch = False )

def update_dictargs( list_of_dicts, master_dict, issuer = 'alberta_treasury' ):
    '''
    Update master_dict. Append union of default_dict and elements of
    list_of_dicts to master_dict.
    '''
    key, default_dict = create_default_dictargs( issuer = issuer )
    if master_dict.get( key, None ) is None:
        master_dict[ key ] = list()
    for append_dict in list_of_dicts:
        d = dict( default_dict.items() + append_dict.items() )
        master_dict[ key ].append( d )
    return master_dict

def gen_dictargs( master_dict ):
    '''
    Generate keywords arguments from master_dict.
    '''
    for key in master_dict:
        for d in master_dict[ key ]:
            yield d

def sort_and_extract( refcoord_regex, extract_regex, \
                    idx_offset = 15, \
                    fp_regex = None, \
                    delete_regex = None, \
                    start_regex = None, \
                    end_regex = None ):
    '''
    Return two functions:
        sort_func to sort rows
        get_func to extract text in a named tuple
    refcoord_regex is the compiled regex to find the reference coordinates.
    extract_regex is the compiled regex to match the text we need.
    fp_regex is the compiled regex to remove the false positives.
    delete_regex, start_regex and end_regex are further arguments
    passed to get_pool_info, along with extract_regex (aka patterns).
    '''
    args_dict = dict( refcoord_regex = refcoord_regex, fp_regex = fp_regex, idx_offset = idx_offset)
    sort_func = set_default_to_sort( **args_dict )
    args_dict = dict( patterns = extract_regex, delete_regex = delete_regex, \
                    start_regex = start_regex, end_regex = end_regex )
    get_func = partial_with_wrapper( get_pool_info, **args_dict )
    return ( sort_func, get_func )

def wrap_extract( get_func, \
                cutoff_list = None, \
                result_type = 'rates', \
                from_dir = 'csv_raw', \
                logging_dir = None ):
    '''
    Return two functions:
        custom_func only works on a single file.
        extract_func works on the directory assigned.
    get_func is the function extracting the text from sort_and_extract.
    cutoff_list, result_type and from_dir are function arguments to
    use with set_extract_default
    '''
    custom_func = partial_with_wrapper( customize_func, get_data_func = get_func )
    extract_func = set_extract_default( func_custom = custom_func, \
                    cutoff_list = cutoff_list, result_type = result_type, \
                    from_dir = from_dir,  logging_dir = logging_dir )
    return ( custom_func, extract_func )

# Big six folders
BIGSIX_TUPLE = ( 'rbc', 'rbc_dominion', 'bmo', 'cibc', 'desjardins', 'national_bank', \
			'national_bank_financial', 'scotia_bank', 'td_bank', 'td_securities' )

# Declare functions to import
__all__ = [ 'find_ref_coord', 'sort_for_info', \
            'set_default_to_sort', 'is_sorted', \
            'get_namedtuple', 'validate_amount', \
            'validate_mtgno', 'validate_dates', \
            'validate_rate', \
            'redo_issuer', 'extract_info', \
            'set_extract_default', 'create_default_dictargs', \
            'update_dictargs', 'gen_dictargs', \
            'sort_and_extract', 'wrap_extract' ]

if __name__ == '__main__':
    print 'Created functions to sort rows and extract text.'
