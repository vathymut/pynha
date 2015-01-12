# -*- coding: utf-8 -*-
"""

@author: Vathy M. Kamulete
"""

import re

# Declare flags to use for REGEX
FLAGS_TO_USE = re.VERBOSE | re.IGNORECASE

# Create REGEX to find reference coordinates
REFRATE_TAG = re.compile(
                    r"""
                    issuer                  # Should be slighty above the rate
                    |                       # French version
                    .*metteur               # Match émetteur
                    """,
                    FLAGS_TO_USE )

REFDATEISSUE_TAG = re.compile(
                    r"""
                    issue\s*?date                   # Match issue date
                    |                               # French version
                    date\s*?.*mission               # Match date d'émission
                    """,
                    FLAGS_TO_USE )

REFDATEDUE_TAG = re.compile(
                    r"""
                    first\s*?payment\s*?due         # Match first payment date
                    |                               # French version
                    pr.*mier\s*?paiement            # Match (date du) premier paiement
                    |
                    1er.*?paiement                  # Match 1er paiement
                    """,
                    FLAGS_TO_USE )

REFDATEINT_TAG = re.compile(
                    r"""
                    adjustment\s*?date?             # Match issue date
                    |                               # French version
                    rajustement.*\s*?taux           # Match (date de) rajustement du taux
                    """,
                    FLAGS_TO_USE )

REFMTGNO_TAG = re.compile(
                    r"""
                    number\s*?of\s*?m(ortgages)?    # Match number of mortgages
                    |                               # French version
                    pr.*ts\s*?hypo(th.caires)?      # Match prets hypothecaires
                    |
                    cr.*ances\s*?hypo(th.caires)?   # Match creances hypothecaires
                    """,
                    FLAGS_TO_USE )

CLSDMTG_TAG = re.compile(
                    r"""
                    closed\s*?mortgage          # Match closed mortgages
                    |
                    hypoth.*caires\s*?ferm      # Match hypothécaires fermés
                    """,
                    FLAGS_TO_USE )

INSNHA_TAG = re.compile(
                    r"""
                    nha.*?insured                       # Math NHA portfolio insured mortgages
                    |
                    assurance\s*?portefeuille\s*?lnh    # Match portefeuille lnh
                    |
                    assurance.+portefeuille             # Match assurance portefeuille
                    """,
                    FLAGS_TO_USE )

INSPRIV_TAG = re.compile(
                    r"""
                    private.*?insured           # Match Private(ly) insured mortgages
                    |
                    gecmic.*?insured            # Match GECMIC insured mortgages
                    |
                    assur.+secteur\s*?priv      # Match assurés par le secteur privé
                    """,
                    FLAGS_TO_USE )

ID_INSURERS_TAG = re.compile(
                    r"""
                    composition.*?mortgage.*?pool   # Match Composition of Mortgage Pool
                    |
                    composition.*?bloc              # Match Composition du bloc
                    """,
                    FLAGS_TO_USE )

CENTRAL_PAYOR_TAG = re.compile(
                    r"""
                    central.*?payor         # Match Composition Central Payor
                    """,
                    FLAGS_TO_USE )

GENWORTH_TAG = re.compile(
                    r"""
                    genworth                # Match GENWORTH
                    |
                    genwortn                # Matches mangled version of GENWORTH
                    |
                    ge.*?capital.*?mort     # Match GE CAPITAL MORTGAGE
                    """,
                    FLAGS_TO_USE )

AIG_TAG = re.compile(
                    r"""
                    aig
                    """,
                    FLAGS_TO_USE )

CANADAGUARANTY_TAG = re.compile(
                    r"""
                    canada.*?guaranty       # Match Canada Guaranty
                    """,
                    FLAGS_TO_USE )

INSURERS_TAG = '\n|'.join( x.pattern for x in [ GENWORTH_TAG, AIG_TAG, CANADAGUARANTY_TAG ] )
INSURERS_TAG = re.compile( INSURERS_TAG, FLAGS_TO_USE)

CMHC_TAG = re.compile(
                    r"""
                    canad.*?mortgage.*?housing.*?corp
                    |
                    canad.*?housing.*?mortgage.*?corp
                    |
                    cmhc
                    |
                    cmwc                    # Sometimes CMHC shows up as CMWC
                    |
                    civfhc                  # Matches mangled version of CMHC
                    |
                    Soci.*?t.*?canadienne.*?hypoth.*?que.*?logement
                    """,
                    FLAGS_TO_USE )

PPLAMNT_TAG = re.compile(
                    r"""
                    principal.*?amou[nt]*?      # Match principal amount
                    |
                    montant.*?global            # Match montant global
                    """,
                    FLAGS_TO_USE )

MBSRATE_TAG = re.compile(
                    r"""
                    mortgage.*?backed.*?securities  # Match mortgage backed securities
                    |
                    lnh.*?rapportant                # Match Titres hypothécaires LNH rapportant
                    """,
                    FLAGS_TO_USE )

PROFILEPCT_TAG = re.compile(
                    r"""
                    percentage.*?profile             # Match percentage profile
                    |
                    profil.*?pourcentage            # Match profil du POURCENTAGE
                    """,
                    FLAGS_TO_USE )

MTGNOEND_TAG = re.compile(
                        r"""
                        maturity\s*?date        # Match maturity date
                        """, FLAGS_TO_USE )

DOLLARVAL_TAG = re.compile(
                        r"""
                        dollar\s*?value         # Match dollar value
                        |
                        valeur.*?dollars        # Match valeurs en dollars
                        """, FLAGS_TO_USE )

MTGDESCRIPTION_TAG = re.compile(
                        r"""
                        description.*?mortgage      # Match Description of Mortgage(s) Loans
                        |
                        description.*?cr.*ance     # Match Description des Créance(s)
                        |
                        description.*?pr.*?ts
                        """, FLAGS_TO_USE )

LOANS_TAG = re.compile(
                        r"""
                        loans                   # Match Loans
                        |
                        pr.*?ts                 # Match prêts
                        """, FLAGS_TO_USE )

# STILL TO DO: FRENCH
SECURITIES_TAG = re.compile(
                        r"""
                        securities              # Match securities
                        """, FLAGS_TO_USE )


# Create REGEX to extract information
RATE_FMT = re.compile(
                    r"""
                    .*?         # any characters - i.e. catches WAC, etc
                    \d{0,2}     # up to 2 digits
                    [\.,]       # '.' or ','
                    \d{1,5}     # digits after decimal point
                    \s*?        # spaces (OPTIONAL)
                    %           # pct sign
                    """,
                    FLAGS_TO_USE )

DATE_FMT = re.compile(
                    r"""
                    [a-z ][a-z \.,]{1,14}?      # month, followed by spaces, ',' and '.' (OPTIONAL)
                    [\di]+?                     # day, digits - also accept 'I'
                    [stndhr\., ]*?              # 1st, 2nd, 3rd, 28th, ',' or '.' (OPTIONAL)
                    [12][\d ]{3,4}              # the year (4 digits)
                    |                           # NOW THE FRENCH REGEX
                    \d{1,2}                     # day, digits
                    [a-z ][a-z\ ., ]*           # month, followed by spaces, ',' and '.' (OPTIONAL)
                    [12][\d ]{3,4}              # the year (4 digits)
                    """,
                    FLAGS_TO_USE )

MTGTOTNO_FMT = re.compile(
                    r"""
                    [1-9][ ]?               # first digit between 1 to 9
                    \d{0,2}[ ]?             # Next two digits
                    [,?\d{1,3}]*            # Up to 3 digits after optional ,
                    """,
                    FLAGS_TO_USE )

POOLNO_FMT = re.compile(
                    r"""
                    [1-9]\d                 # first 2 digits
                    -?\d{3}                 # Next 3 digits, with optional -
                    -?\d{3}                 # Next 3 digits, with optional -
                    """,
                    FLAGS_TO_USE  )

DECIMAL_FMT = re.compile(
                    r"""
                    \d+                 # one or more digits
                    \.                  # Decimal point
                    \d+                 # one or more digits after decimal
                    """,
                    FLAGS_TO_USE  )

CLSDMTG_AMOUNT_FMT = re.compile(
                    r"""
                    \d+[, \.\d]*       # Match optional space, '.' or comma ','
                    """,
                    FLAGS_TO_USE )

ZEROS_FMT = re.compile(
                    r"""
                    0\.0+
                    """,
                    FLAGS_TO_USE )

HUNDREDS_FMT = re.compile(
                    r"""
                    100\.0+
                    """,
                    FLAGS_TO_USE )

RATE_FP_FMT = re.compile(
                    r"""
                    \d{0,2}     # up to 2 digits
                    [\.,]       # '.' or ','
                    \d{1,5}     # digits after decimal point
                    \s*         # spaces (OPTIONAL)
                    %           # pct sign
                    """,
                    FLAGS_TO_USE )

PERCENT_FMT = re.compile(
                    r"""
                    %
                    """, FLAGS_TO_USE)

if __name__ == '__main__':
    print 'Created regexes'
