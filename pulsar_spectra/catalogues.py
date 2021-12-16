"""
Loads all the data required by vcstools from the data directory.
"""

import os
import re
import glob
import psrqpy

# Hard code the path of the flux catalouge directories
CAT_DIR = os.path.join(os.path.dirname(__file__), 'catalouges')

# Grab all the catalogue yamls
CAT_YAMLS = glob.glob("{}/*yaml".format(CAT_DIR))

# Hard code the path of the ATNF psrcat database file
ATNF_LOC = os.path.join(CAT_DIR, 'psrcat.db')

def flux_from_atnf(pulsar, query=None, assumed_error=0.5):
    """Queries the ATNF database for flux and spectral index info on a particular pulsar at all frequencies

    Parameters
    ----------
    pulsar : `str`
        The Jname of the pulsar.
    query : psrqpy object, optional
        A previous psrqpy.QueryATNF query. Can be supplied to prevent performing a new query.
    assumed_error : `float`, optional
        If no error found, apply this factor to flux to make an assumed error. |b| Default: 0.5.

    Returns
    -------
    freq_all : `list`
        All frequencies in Hz with flux values on ATNF.
    flux_all : `list`
        The flux values corresponding to the freq_all list in mJy.
    flux_err_all : `list`
        The uncertainty in the flux_all values.
    spind : `float`
        The spectral index from ATNF, will be None if not available.
    spind_err : `float`
        The ucnertainty in spind from ATNF, will be None if not available.
    """
    if query is None:
        query = psrqpy.QueryATNF(psrs=[pulsar], loadfromdb=ATNF_LOC).pandas
        print(ATNF_LOC)
    query_id = list(query['PSRJ']).index(pulsar)

    # Find all flux queries from keys
    flux_queries = []
    for table_param in query.keys():
        if re.match("S\d*\d$", table_param) or re.match("S\d*G$", table_param):
            flux_queries.append(flux_queries)

    freq_all     = []
    flux_all     = []
    flux_err_all = []
    references   = []
    # Get all available data from dataframe and check for missing values
    for flux_query in flux_queries:
        flux = query[flux_query][query_id]
        
        # Check for flux
        if not np.isnan(flux):
            flux_all.append(flux) # in mJy

            # Check for flux error. Sometimes error values don't exist, causing a key error in pandas
            try:
                flux_err = query[flux_query+"_ERR"][query_id]
                if flux_err == 0.0:
                    logger.debug("{0} flux error for query: {1}, is zero. Assuming 20% uncertainty"\
                                 .format(pulsar, flux_query))
                    flux_err = flux*assumed_error
            except KeyError:
                logger.debug("{0} flux error value {1}, not available. assuming 20% uncertainty"\
                             .format(pulsar, flux_query))
                flux_err = flux*assumed_error

            if np.isnan(flux_err):
                logger.debug("{0} flux error value for {1} not available. assuming 20% uncertainty"\
                             .format(pulsar, flux_query))
                flux_err = flux*assumed_error
            flux_err_all.append(flux_err) # in mJy

            # Converts key to frequency in MHz
            if flux_query.endswith("G"):
                # In GHz to convert to MHz
                freq = int(flux_query[1:])*1e3
            else:
                freq = int(flux_query[1:])
            freq_all.append(freq) 

            # Grab reference code
            references.append(query[flux_query+"_REF"][query_id])

    return freq_all, flux_all, flux_err_all, references