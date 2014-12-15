# -*- coding: utf-8 -*-
"""

@purpose: Download the pdf files for the NHA-MBS circulars.
@author: Vathy M. Kamulete
"""

from ioFunc import create_issuer_dir, check_if_dir_to_visit, goto_pdf_dir, gen_issuer_names
import ioFunc # Set the global variables in module later
from urlparse import urljoin, urlsplit
from urllib2 import urlopen, Request
from time import sleep
import shutil
import datetime
from fnmatch import filter # Use glob.glob instead
from os import chdir, listdir, getcwd
from os.path import dirname, abspath, join, splitext, basename

def get_links_from_file( filename ):
	"""
	Get links/urls from the filename
	"""
	with open( filename, 'r') as f:
		for url in f:
			yield url

def give_filename( url_rel ):
    """
    Give the pdf a filnename.
	Append time information to the filename.
    """
    filename = basename( url_rel )
	# Add time information
    now_datetime = datetime.datetime.now( )
    now_string = now_datetime.strftime( "%Y-%m-%d-%H-%M-%S" )
    if filename.endswith( '.pdf' ):
		fileno, ext_pdf = splitext( filename )
		pdf_filename = fileno + '-' + now_string + ext_pdf
		return pdf_filename

def check_if_downloaded( url, debug_print = True ):
	"""
	Check if pdf file has already been downloaded.
	"""
	# Get pdf filename
	filename = basename( url )
	fileno, ext_pdf = splitext( filename )
	for file in listdir( getcwd() ):
		if fileno in file:
			if debug_print:
				print 'Skipping %s' % ( filename )
			return True
	return False

def download_pdf( url, filename = None ):
    """
    Download and name the pdf file
    """
    r = urlopen( Request( url ) )
    try:
        if filename is None:
            filename = give_filename( url )
        with open( filename, 'wb' ) as f:
            shutil.copyfileobj( r, f )
    finally:
        r.close()

def get_filename_and_url( filenames ):
	"""
	Transform nested for loop into 1D loop.
	Returns tuple of filename and url being iterated over.
	"""
	for filename in filenames:
		for url in get_links_from_file( filename ):
			 yield ( filename, url )

# Set home Directory
MAINDIR = dirname( dirname( abspath( __file__ ) ) )
HOMEDIR = join( MAINDIR, 'pynha_scraper' )
ioFunc.HOMEDIR  = HOMEDIR
# Website url
BASEURL = 'http://www.cmhc-schl.gc.ca'

# Get all files in ~/pynha_scraper, including txt files with links
chdir( HOMEDIR )
all_filenames = listdir( HOMEDIR )

# Keep all .txt files
pattern = '*.txt'
issuers_filenames = filter( all_filenames, pattern )

if __name__ == '__main__':
    # Get all issuers, including Big Six
    ISSUER_DIRS = list( gen_issuer_names( skip_list = None ) )
    # If limiting to specific issuers, uncomment line below and set issuers
    ## ISSUER_DIRS = ( 'rbc', 'rbc_dominion' )
    for filename, url in get_filename_and_url( issuers_filenames ):
		new_issuer_dir = create_issuer_dir( filename, prefix_path = 'pdf_downloaded' )
		if not check_if_dir_to_visit( new_issuer_dir, ISSUER_DIRS ):
			continue
		with goto_pdf_dir( new_issuer_dir, HOMEDIR ):
			url = url.rstrip()
			abs_link = urljoin( BASEURL, url = url )
			pdf_filename = give_filename( url_rel = url )
			if check_if_downloaded( url ):
				continue
			download_pdf( abs_link, pdf_filename )
			print 'in directory:' , getcwd()
			sleep( 3 )