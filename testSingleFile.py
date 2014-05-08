# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 08:34:30 2013

@author: Vathy M. Kamulete
"""

from stdDataFunc import get_csvrows
from os.path import dirname, abspath, basename
from os import chdir
from setUpEnv import gen_refcoord_and_cutoff

# csv headers
HEADERS = [ 'page_no', 'obj_no', 'x0', 'y0', 'x1', 'y1', 'text' ]

def test_csv_file( csv_filename, func_apply, cutoff_list, \
                refcoord_list = None, \
                absdist_tuple = (-25.0, -25.0), \
                headers = HEADERS, \
                skip_rows_no = 0, \
                stop_row_no = 120 ):
    '''
    Use func_apply on file csv_filename and return info.
    func_apply could be:
        custom_rate, custom_date_issue, custom_date_due
    cutoff_list, refcoord_list and absdist_tuple are arguments to func_apply.
    headers, skip_rows and stop_rows are arguments to gen_id_csvrows.
    '''
    is_given = refcoord_list is not None
    args_dict = dict( filename = csv_filename, headers = headers, \
                    skip_rows_no = skip_rows_no, stop_row_no = stop_row_no )
    rows_list = get_csvrows( **args_dict )
    args_dict = dict( func_custom = func_apply, cutoff_list = cutoff_list, refcoord_list = refcoord_list )
    for idx, func in enumerate( gen_refcoord_and_cutoff( **args_dict ) ):
        print '\n\t\tIndex: %d -- Reference coordinates given: %s' % ( idx, is_given )
        try:
            func( rows_list, csv_filename, absdist_tuple = absdist_tuple )
        except ( ValueError, TypeError ) as err:
            print err.message
