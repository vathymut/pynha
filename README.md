## Synopsis

These scripts written in Python are meant to:

- Download the pdf files for NHA-MBS circulars.
- Convert said pdf files to csv files.
- Contain functions that extract useful information from these files.

These scripts assume that a scraper/spider has already gathered all the links to the pdf files. These links have been saved in the folder:

> ~/pynha_scraper

For each issuer, the corresponding txt file in this folder contains the links to its circulars.

Once dowloaded, the pdf are saved in the folder:

> ~/pynha_scraper/pdf_downloaded

## Requirements

With Python 2.7, you need:

- pandas >= 0.9.0
- pdfminer >= 20140328

## Usage

To download NHA-MBS circulars (pdf) and save as files, run:

    python downloadIssuersPdf.py

To convert pdf files to csv, run:

    python convertToCsv.py


## Motivation

Create a dataset for NHA-MBS (Mortgage-backed securities insured by the Canadian Governement) from the circulars.
