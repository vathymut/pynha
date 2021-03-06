# -*- coding: utf-8 -*-
"""

@author: Vathy M. Kamulete
"""

from os import walk
from os.path import dirname, join, abspath, basename
from stdDataFunc import partial_with_wrapper
from time import sleep
import pandas as pd

def gen_csv_and_issuer( result_dir = 'rates' ):
    """
    Walk the directory tree of result_dir and generates
    the csv path of the parsed results along with the corresponging issuers.
    result_dir can be:
        'mtgtotno', 'date_due', 'date_issue',
        'date_int', 'rates', etc
    """
    # HOMEDIR is a global variable (set elsewhere)
    start_dir = join( HOMEDIR, result_dir )
    for dirpath, _, filenames in walk( start_dir ):
        for f in filenames:
            filepath, dir_issuer = join( dirpath, f ), basename( dirpath )
            yield filepath, dir_issuer

def set_keys_to_df( csv_filepath, issuer ):
    """
    Set keys to dataframe as poolno and issuer.
    """
    df = pd.read_csv( csv_filepath )
    df[ 'issuer' ] = issuer
    df.set_index( [ 'poolno', 'issuer' ], inplace = True )
    return df

def concat_df( result_dir = 'rates' ):
    """
    Concatenate dataframes in result_dir folder
    into a single dataframe.
    """
    df_list = list()
    for csv_filepath, issuer in gen_csv_and_issuer( result_dir = result_dir ):
        df = set_keys_to_df( csv_filepath, issuer )
        df_list.append( df )
    return pd.concat( df_list )

def concat_df_from_list( dir_list ):
    """
    Return list of dataframes for each element in dir_list.
    """
    return map( concat_df, dir_list )

def merge_df_from_list( df_list, how = 'outer', left_index = True, \
                        right_index = True, sort = True ):
    """
    Merge dataframes in df_list.
    """
    kwargs = dict( how = how, left_index = left_index, right_index = right_index, sort = sort )
    merge_func = partial_with_wrapper( pd.merge, **kwargs )
    df = reduce( merge_func, df_list )
    return df.groupby( level = [ 'poolno', 'issuer' ] ).first( )

# Declare functions to import
__all__ = [ 'concat_df', 'concat_df_from_list', 'concat_df_from_list', 'merge_df_from_list' ]
