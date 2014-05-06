# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 08:34:30 2013

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

def test_sort( csv_filename, sort_func, cutoff_tuple, \
                refcoord_list = None, \
                absdist_tuple = (-25.0, -25.0), \
                headers = HEADERS, \
                skip_rows_no = 0, \
                stop_row_no = 120 ):
    '''
    Use func_apply on file csv_filename and return info.
    sort_func could be:
        sort_rate, sort_privamt, etc
    cutoff_list, refcoord_list and absdist_tuple are arguments to func_apply.
    headers, skip_rows and stop_rows are arguments to gen_id_csvrows.
    '''
    print 'Testing sort function'
    args_dict = dict( skip_rows_no = skip_rows_no, stop_row_no = stop_row_no )
    rows_list = get_csvrows( csv_filename, headers, **args_dict )
    print 'Sort by reference coordinates: \n'
    args_dict = dict( cutoff_tuple = cutoff_tuple, absdist_tuple = absdist_tuple )
    try:
        sorted_rows = sort_func( rows_list, **args_dict )
        print ''.join( [ x.text for x in sorted_rows ] )
    except ( ValueError, ) as err:
        print err.message

def test_extract( csv_filename, extract_func, cutoff_tuple, \
                refcoord_list = None, \
                absdist_tuple = (-25.0, -25.0), \
                headers = HEADERS, \
                skip_rows_no = 0, \
                stop_row_no = 120 ):
    '''
    Use func_apply on file csv_filename and return info.
    extract_func could be:
        get_rate, get_privamt, etc
    cutoff_list, refcoord_list and absdist_tuple are arguments to func_apply.
    headers, skip_rows and stop_rows are arguments to gen_id_csvrows.
    '''
    args_dict = dict( skip_rows_no = skip_rows_no, stop_row_no = stop_row_no )
    rows_list = get_csvrows( csv_filename, headers, **args_dict )
    print 'Testing function:', extract_func.__name__
    try:
        result = extract_func( rows_list, cutoff_tuple = cutoff_tuple )
        print 'Without reference coordinates:', result
    except ( ValueError, ) as err:
        print err.message

# Test functions
if __name__ == '__main__' :
    from makeInsPrivAmount import sort_privamt, get_privamt, extract_privamt
    from makeInsFmtSafe import sort_insnha, sort_inspriv
    from makeInsAmount import get_insnha, get_inspriv
    from makeInsAmount_v3 import sort_ins_list, get_insall_v3
    from listOfCutoffCoord import DESC_CUTOFFS, PPL_AMOUNT_CUTOFFS, \
                            DATE_DUE_CUTOFFS, DATE_ISSUE_CUTOFFS
    csv_filename = r'B:\pynha_ins\csv_raw\macquarie\97523641-2013-12-02-18-10-04.csv'
    args_dict = dict( csv_filename = csv_filename, cutoff_tuple = ( 250.0, 10 ), \
                    stop_row_no = 250, absdist_tuple = ( -25.0, -25.0 ) )
    # Testing sorting function
    test_sort( sort_func = sort_ins_list, **args_dict )
    # Testing extract function
    test_extract( extract_func = get_insall_v3, **args_dict )

