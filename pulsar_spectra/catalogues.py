"""
Loads all the data required by vcstools from the data directory.
"""

import os
import re
import glob
import yaml
import psrqpy
import numpy as np

# Hard code the path of the flux catalouge directories
CAT_DIR = os.path.join(os.path.dirname(__file__), 'catalouges')

# Grab all the catalogue yamls
CAT_YAMLS = glob.glob("{}/*json".format(CAT_DIR))

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
    references : `list`
        The reference keys from:
        https://www.atnf.csiro.au/research/pulsar/psrcat/psrcat_ref.html
    """
    if query is None:
        query = psrqpy.QueryATNF(psrs=[pulsar], loadfromdb=ATNF_LOC).pandas
        print(ATNF_LOC)
    query_id = list(query['PSRJ']).index(pulsar)

    # Find all flux queries from keys
    flux_queries = []
    for table_param in query.keys():
        if re.match("S\d*\d$", table_param) or re.match("S\d*G$", table_param):
            flux_queries.append(table_param)

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


def collect_catalogue_fluxes():
    """Collect the fluxes from all of the catalogues recorded in this repo.

    Returns
    -------
    jname_cat_dict[jname][ref]['Frequency MHz', 'Flux Density mJy', 'Flux Density error mJy'] : `dict`
        `jname` : `str`
            The pulsar's Jname.
        `ref` : `str`
            The reference label.
        ``'Frequency MHz'``
            The observing frequency in MHz.
        ``'Flux Density mJy'``
            The flux density in mJy.
        ``'Flux Density error mJy'`
            The error of the flux density in mJy.
    jname_cat_list[jname] : `dict`
        `jname` : `str`
            The pulsar's Jname.
        Each dictionary contains a list of lists of ['Frequency MHz', 'Flux Density mJy', 'Flux Density error mJy', 'ref']
            ``'Frequency MHz'``
                The observing frequency in MHz.
            ``'Flux Density mJy'``
                The flux density in mJy.
            ``'Flux Density error mJy'`
                The error of the flux density in mJy.
            `ref` : `str`
                The reference label.
    """
    # Make a dictionary for each pulsar
    query = psrqpy.QueryATNF(params=['PSRJ'], loadfromdb=ATNF_LOC).pandas
    jnames = list(query['PSRJ'])
    jname_cat_dict = {}
    jname_cat_list = {}
    for jname in jnames:
        jname_cat_dict[jname] = {}
        # freq, flux, flux_err, references
        jname_cat_list[jname] = [[],[],[],[]]

    # Loop over catalogues and put them into the database
    for cat_file in CAT_YAMLS:
        cat_label = cat_file.split("/")[-1].split(".")[0]

        # Load in the dict
        with open(cat_file, "r") as stream:
            cat_dict = yaml.safe_load(stream)

        # Find which pulsars in the dictionary
        for jname in jnames:
            if jname in cat_dict.keys():
                # Update dict
                jname_cat_dict[jname][cat_label] = cat_dict[jname]
                # Update list
                jname_cat_list[jname][0] += cat_dict[jname]['Frequency MHz']
                jname_cat_list[jname][1] += cat_dict[jname]['Flux Density mJy']
                jname_cat_list[jname][2] += cat_dict[jname]['Flux Density error mJy']
                jname_cat_list[jname][3] += [cat_label] * len(cat_dict[jname]['Frequency MHz'])

    return jname_cat_dict, jname_cat_list

            