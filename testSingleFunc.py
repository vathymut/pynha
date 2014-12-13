# -*- coding: utf-8 -*-
"""

@author: Vathy M. Kamulete
"""

from stdDataFunc import get_csvrows
from os.path import dirname, abspath, basename
from os import chdir
from setUpEnv import gen_refcoord_and_cutoff

# Home Directory - On RZ machine: 'B:\\nha_mbs'
HOMEDIR = dirname( dirname( abspath( __file__ ) ) )
# pynha Directory - On RZ machine: 'B:\\nha_mbs\\pynha'
PYNHADIR = dirname( abspath( __file__ ) )
# csv headers
HEADERS = [ 'page_no', 'obj_no', 'x0', 'y0', 'x1', 'y1', 'text' ]

def test_func( csv_filename, \
                func, \
                kwargs_func = None, \
                headers = HEADERS, \
                skip_rows_no = 0, \
                stop_row_no = 120 ):
    """
    Use func on file csv_filename and return info.
    headers, skip_rows and stop_rows are arguments to gen_id_csvrows.
    """
    print 'Testing function'
    kwargs = dict( skip_rows_no = skip_rows_no, stop_row_no = stop_row_no )
    rows_list = get_csvrows( csv_filename, headers, **kwargs )
    try:
        if kwargs_func is None:
            result = func( rows_list )
        else:
            result = func( rows_list, **kwargs_func )
        print result
        return result
    except ( ValueError, ) as err:
        print err.message

def test_sort( csv_filename, \
                sort_func, \
                cutoff_tuple, \
                refcoord_list = None, \
                absdist_tuple = (-25.0, -25.0), \
                headers = HEADERS, \
                skip_rows_no = 0, \
                stop_row_no = 120 ):
    """
    Use sort_func on file csv_filename and return info.
    sort_func could be:
        sort_rate, sort_privamt, etc
    cutoff_list, refcoord_list and absdist_tuple are arguments to func_apply.
    headers, skip_rows and stop_rows are arguments to gen_id_csvrows.
    """
    print 'Testing sort function'
    args_dict = dict( skip_rows_no = skip_rows_no, stop_row_no = stop_row_no )
    rows_list = get_csvrows( csv_filename, headers, **args_dict )
    print 'Sort by reference coordinates: \n'
    args_dict = dict( cutoff_tuple = cutoff_tuple, absdist_tuple = absdist_tuple )
    try:
        sorted_rows = sort_func( rows_list, **args_dict )
        print ''.join( [ x.text for x in sorted_rows ] )
        return sorted_rows
    except ( ValueError, ) as err:
        print err.message

def test_extract( csv_filename, \
                extract_func, \
                cutoff_tuple, \
                refcoord_list = None, \
                absdist_tuple = (-25.0, -25.0), \
                headers = HEADERS, \
                skip_rows_no = 0, \
                stop_row_no = 120 ):
    """
    Use func_apply on file csv_filename and return info.
    extract_func could be:
        get_rate, get_privamt, etc
    cutoff_list, refcoord_list and absdist_tuple are arguments to func_apply.
    headers, skip_rows and stop_rows are arguments to gen_id_csvrows.
    """
    kwargs = dict( skip_rows_no = skip_rows_no, stop_row_no = stop_row_no )
    rows_list = get_csvrows( csv_filename, headers, **kwargs )
    print 'Testing function:', extract_func.__name__
    try:
        kwargs = dict( cutoff_tuple = cutoff_tuple, absdist_tuple = absdist_tuple )
        result = extract_func( rows_list, **kwargs )
        print 'Without reference coordinates:', result
        return result
    except ( ValueError, ) as err:
        print err.message


