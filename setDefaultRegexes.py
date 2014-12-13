# -*- coding: utf-8 -*-
"""

@author: Vathy M. Kamulete
"""

from stdDataFunc import get_pool_info, partial_with_wrapper
import re

########################## DEPRECATED ##########################

# False positives to remove for total number of mortgages.
_REGEXES_LIST = [ COMPILED_POOLNO, COMPILED_DATE, COMPILED_DECIMAL ]
_REGEX_FP = '\n|\n'.join( regex.pattern for regex in _REGEXES_LIST )
COMPILED_MTGNO_FP = re.compile( _REGEX_FP, FLAGS_TO_USE )

# False positives to remove for dollar value of closed mortgages.
_REGEXES_LIST= [ COMPILED_HUNDREDS, COMPILED_ZEROS, COMPILED_RATE_FP ]
_REGEX_FP = '\n|\n'.join( regex.pattern for regex in _REGEXES_LIST )
COMPILED_CLSDMTG_FP = re.compile( _REGEX_FP, FLAGS_TO_USE )

### Set function default to get pool information
# Dates
args_dict = dict( patterns = COMPILED_DATE, delete_regex = COMPILED_DECIMAL )
get_idpool_dates = partial_with_wrapper( get_pool_info, **args_dict )
# Total no. of mortgages
args_dict = dict( patterns = COMPILED_MTGTOTNO, delete_regex = COMPILED_MTGNO_FP )
get_idpool_mtgno = partial_with_wrapper( get_pool_info, **args_dict )
# Total no. of mortgages -- EXPOSED VERSION
from stdDataFuncCustom import COMPILED_REFDATEISSUE_TAG, COMPILED_REFDATEINT_TAG
args_dict = dict( patterns = COMPILED_MTGTOTNO, delete_regex = COMPILED_MTGNO_FP, \
                start_regex = COMPILED_REFDATEISSUE_TAG, end_regex = COMPILED_REFDATEINT_TAG )
get_idpool_mtgno_exposed = partial_with_wrapper( get_pool_info, **args_dict )
# Amount of closed mortgages
args_dict = dict( patterns = COMPILED_CLSDMTG_AMOUNT, end_regex = COMPILED_PROFILEPCT_TAG )
get_desc_clsdmtg = partial_with_wrapper( get_pool_info, **args_dict )
# Amount of principal -- should be same amount as closed mortgages
args_dict = dict( patterns = COMPILED_CLSDMTG_AMOUNT, delete_regex = COMPILED_RATE )
get_desc_pplamnt = partial_with_wrapper( get_pool_info, **args_dict )

# Declare functions to import
__all__ = [ 'get_idpool_dates', \
            'get_idpool_mtgno', 'get_idpool_mtgno_exposed', \
            'get_desc_clsdmtg', 'get_desc_pplamnt' ]

