# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 08:34:30 2013

@author: Vathy M. Kamulete
"""

### pdf-miner requirements

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from itertools import chain

def with_pdf( pdf_path, pdf_pwd = '' ):
	'''
	Open the pdf document; the file is not password-protected.
	If it is, pdf_pwd is the password. Return the pdfminer doc.
	'''
	fp = open( pdf_path, 'rb' )
	# create a parser object associated with the file object
	parser = PDFParser( fp )
	# create a PDFDocument object that stores the document structure
	doc = PDFDocument( parser )
	# supply the password for initialization
	doc.initialize( pdf_pwd )
	# check that doc is extractable
	if doc.is_extractable:
		return doc

def get_pages( pdf_doc, pages_to_parse = None ):
    '''
    Only parse the pdf pages in pages_to_parse.
	If pages_to_parse is None, get all the pages.
    pages_to_parse should be a tuple.
    '''
    for page_no, page in enumerate( PDFPage.create_pages( pdf_doc ) ):
        if pages_to_parse is None:
            yield page_no, page
        else:
            if page_no in pages_to_parse:
                yield page_no, page
            else:
                continue

def set_up_interpreter( ):
	'''
	Set up pdf interpreter and device to extract layout of pages.
	Simply takes care of overhead.
	'''
	rsrcmgr = PDFResourceManager( )
	# Set parameters for analysis.
	laparams = LAParams()
	device = PDFPageAggregator( rsrcmgr, laparams=laparams )
	interpreter = PDFPageInterpreter( rsrcmgr, device )
	return device, interpreter

def get_pdf_layout( pdf_page ):
    '''
    Return the layout of the pdf page. Takes care of overhead.
    '''
    device, interpreter = set_up_interpreter( )
    interpreter.process_page( pdf_page )
    layout = device.get_result( )
    return layout

def to_bytestring( s, enc='ascii', error='replace' ):
    """
    Convert the given unicode string to a bytestring using the standard
    encoding (ascii).
    """
    if s:
        if isinstance(s, str):
            return s.decode( enc, error )
        else:
            # replace ? by spaces
            return s.encode( enc, error ).replace( '?', ' ' )
    else:
        return 'No text'

def process_lt_obj( layout ):
	'''
	Process each lt_obj.
	Return tuple (obj_no, bbox_coordinates, text) to be written to csv.
	'''
	for obj_no, obj in enumerate( layout ):
		result_list = []
		result_list.append( obj_no )
		result_list.extend( obj.bbox )
		result_list.append( process_text( obj ) )
		yield result_list

def process_text( obj ):
	'''
	Extract the text from the pdf object.
	If obj has no text, return the empty string.
	'''
	try:
		unicode_text = obj.get_text( )
		return to_bytestring( unicode_text )
	except AttributeError:
		# if obj doesn't have get_text() method
		empty_string = ''
		return empty_string

def generate_rows( pdf_doc, pages_to_parse ):
	'''
	Return tuples ( page_no, obj_no, bbox_coordinates, text )
	to be written to csv for all pages in pages_to_parse.
	'''
	for page_no, page in get_pages( pdf_doc, pages_to_parse ):
		layout = get_pdf_layout( page )
		for csv_row_list in process_lt_obj( layout ):
			csv_row_list.insert( 0,  page_no )
			yield csv_row_list

def gen_rows_frompath( from_pdf_path, pages_to_parse ):
	'''
	Convenient wrapper around generate_rows.
	It takes the path as opposed to the pdf document.
	'''
	pdfminer_doc = with_pdf( from_pdf_path )
	for csv_row_list in generate_rows( pdfminer_doc, pages_to_parse ):
		yield csv_row_list

## pdfminer_doc = with_pdf( pdf_path )
## page_gen = get_pages( pdfminer_doc, PAGES_TO_PARSE )
## page_no, page = next( page_gen )
## layout = get_pdf_layout( page )
## obj_gen = enumerate( layout )
## obj_no, obj = next( obj_gen )
## pprint( obj.__dict__ )
## obj_no, obj = next( obj_gen ); pprint( obj.__dict__ )

from pprint import pprint
if __name__ == '__main__':
    # Test case
    pdf_path = r'B:\pynha_scraper\pdf_downloaded\home_trust\96602560-2013-12-02-01-10-27.pdf'
    PAGES_TO_PARSE = ( 0, 1, 2, 3 )
    for csv_row_list in gen_rows_frompath( pdf_path, PAGES_TO_PARSE ):
        print csv_row_list

