# -*- coding: utf-8 -*-
"""
Created on 26/04/2014

@author: Vathy M. Kamulete
"""
import string
from stdDataFunc import trim_text, extract_text

def count_instances( string_to_test, types = string.digits ):
    """
    Count the number of types (digits) found in the string string_to_test.
    """
    string_as_list = list( string_to_test )
    string_list_filtered = filter( lambda x: x in types, string_as_list )
    return len( string_list_filtered )

def count_digits_and_letters( string_to_test, \
                            digits = string.digits, \
                            letters = string.ascii_letters ):
    """
    Count the number of types (digits) found in the string string_to_test.
    """
    no_digits = count_instances( string_to_test, types = digits )
    no_letters = count_instances( string_to_test, types = letters )
    return ( no_digits, no_letters )

def check_consecutive( rows ):
    """
    Return True if the rows are consecutive based on attribute obj_no.
    """
    rows_idx = [ int( row.obj_no ) for row in rows ]
    return rows_idx == range( rows_idx[0], rows_idx[-1] + 1 )

def check_newlines( rows, count_max = 2 ):
    """
    Return True if all rows have less than count_max newline characters.
    """
    newlines_count = [ row.text.count( '\n' ) for row in rows ]
    newlines_bool = [ row_count < count_max for row_count in newlines_count ]
    return all( newlines_bool )

def match_any_re( rows_lines, regex_list ):
    """
    Return True if text in rows_lines matches any of the regex in regex_list.
    Note: regex in regex_list should be compiled.
    """
    return any( regex.search( rows_lines ) for regex in regex_list )

def validate_re( rows, regex_list ):
    """
    Return True if all rows match at least one regex in regex_list.
    """
    bool_re = [ match_any_re( r.text, regex_list ) for r in rows ]
    if all( bool_re ):
        return rows
    print 'Rows:\n', rows
    raise ValueError( "Some rows don't contain the requisite regex." )

def validate_newlines( rows, count_max = 2 ):
    """
    Return rows if it passes format check for number of newline characters.
    """
    bool_newlines = check_newlines( rows, count_max = count_max )
    if bool_newlines:
        return rows
    print 'Rows:\n', rows
    error_print = "Some rows have %d or more newline characters." % count_max
    raise ValueError( error_print )

def validate_consecutive( rows, rows_length = 4 ):
    """
    Return rows if it passes format check for consecutive rows.
    """
    if check_if_consecutive( rows, rows_length = rows_length ):
        return rows
    print 'Rows:\n', rows[:rows_length]
    raise ValueError( "The rows are not consecutive." )

def validate_amount( result_list, \
                    min_digits = 6, \
                    max_digits = 15, \
                    max_letters = 3 ):
    """
    Return result_list if it passes format check for dollar amount.
    """
    mum_list = [ count_instances(r, types = string.digits) for r in result_list ]
    is_num = [ max_digits > num > min_digits for num in mum_list ]
    str_list = [ count_instances(r, types = string.ascii_letters) for r in result_list ]
    is_not_ltr = [ max_letters > ltr for ltr in str_list ]
    if any( is_num ) and all( is_not_ltr ):
        return result_list
    print 'Result list:\n', result_list
    error_print = "The amounts in the list are not formatted as they should be."
    raise ValueError( error_print )

def validate_blanks( result_list, \
                    max_digits = 1, \
                    max_letters = 3 ):
    """
    Return result_list if it passes format check for blanks (i.e N/A, spaces, etc).
    """
    mum_list = [ count_instances(r, types = string.digits) for r in result_list ]
    is_not_num = [ max_digits > num for num in mum_list ]
    str_list = [ count_instances(r, types = string.ascii_letters) for r in result_list ]
    is_not_ltr = [ max_letters > ltr for ltr in str_list ]
    if all( is_not_num ) and all( is_not_ltr ):
        return result_list
    error_print = "The elements in the list are not blank."
    raise ValueError( error_print )

def validate_mtgno( result_list, \
                    types = string.digits, \
                    min_digits = 1, \
                    max_digits = 5 ):
    """
    Return result_list if it passes format check for mortgage number.
    """
    mum_list = [ count_instances(result, types = types) for result in result_list ]
    bool_list = [ max_digits >= num and num >= min_digits for num in mum_list ]
    if any( bool_list ):
        return result_list
    print 'Mortgage no.:\n', result_list
    error_print = "The number of mortgages is %d digits or less or %d digits or more." % ( min_digits, max_digits )
    raise ValueError( error_print )

def validate_dates( result_list, \
                    min_digits = 4, \
                    max_digits = 8, \
                    min_letters = 3, \
                    max_letters = 12 ):
    """
    Return result_list if it passes format check for dates.
    """
    num_and_letters = [ count_digits_and_letters(l) for l in result_list ]
    digits_fmt = [ max_digits > num >= min_digits for num, _ in num_and_letters ]
    letters_fmt = [ max_letters > letters >= min_letters for _, letters in num_and_letters ]
    if all( digits_fmt ) and all( letters_fmt ):
        return result_list
    print 'Dates:\n', result_list
    raise ValueError( "The dates do not all pass the format check." )

def validate_rate( result_list, \
                    types = string.digits, \
                    min_digits = 1, \
                    max_digits = 7 ):
    """
    Return result_list if it passes format check for dollar amount.
    """
    mum_list = [ count_instances(result, types = types) for result in result_list ]
    bool_list = [ max_digits >= num > min_digits for num in mum_list ]
    if any( bool_list ):
        return result_list
    print 'Rates list:\n', result_list
    error_print = "The rate is %d digits or less or %d digits or more." % ( min_digits, max_digits )
    raise ValueError( error_print )

def filter_nonempty( sorted_rows ):
    """
    Return rows in sorted_rows that are not empty.
    """
    sorted_rows = sorted( sorted_rows, key = lambda row: float(row.obj_no) )
    filtered_rows = [ r for r in sorted_rows if not r.text == '' ]
    if not filtered_rows:
        print 'Rows:\n', sorted_rows
        raise ValueError( "Filtering rows returns an empty list." )
    return filtered_rows

def abort_re( rows, regex_list ):
    """
    Return rows if they don't contain any regex in regex_list.
    """
    if regex_list is None:
        return rows
    rows_lines = extract_text( rows )
    re_bool = match_any_re( rows_lines, regex_list )
    if not re_bool:
        return rows
    print 'Rows:\n', rows
    raise ValueError( 'Contains regex to abort parsing.' )

def filter_re( rows, regex_list, remove_rows = True ):
    """
    Return rows if they do not match any regex in regex_list.
    if remove_rows is False, return rows that do match any regex in regex_list.
    """
    if regex_list is None:
        return rows
    if remove_rows:
        f_rows = [ r for r in rows if not match_any_re( r.text, regex_list ) ]
    else:
        f_rows = [ r for r in rows if match_any_re( r.text, regex_list ) ]
    if not f_rows:
        raise ValueError( "Filtering rows returns an empty list." )
    return f_rows

def filter_all( rows, \
                rows_length = None, \
                abort_re_list = None, \
                rm_re_list = None, \
                keep_re_list = None ):
    """
    Return rows if the row passes the format check.
    """
    f_rows = filter_nonempty( rows )
    f_rows = abort_re( f_rows, abort_re_list )
    f_rows = filter_re( f_rows, rm_re_list, remove_rows = True )
    f_rows = filter_re( f_rows, keep_re_list, remove_rows = False )
    if rows_length is not None:
        f_rows = f_rows[:rows_length]
    if not f_rows:
        print 'Rows:\n', rows
        raise ValueError( "Filtering rows returns an empty list." )
    return f_rows

def trim_rows( sorted_rows, start_regex = None, end_regex = None ):
    """
    Return list with text from sorted_rows.
    Ignore any text preceding the regex start_regex.
    Ignore any text after the regex end_regex.
    """
    try:
        text_rows = [ row.text for row in sorted_rows ]
        text_rows = [ trim_text( txt, start_regex = start_regex, end_regex = end_regex ) for txt in text_rows ]
        return text_rows
    except ( ValueError, ) as err:
        print 'Text:', [ row.text for row in sorted_rows ]
        raise err

if __name__ == '__main__':
    print 'Created functions to validate inputs and outputs.'