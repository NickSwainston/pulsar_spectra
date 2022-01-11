"""
Loads all the data required by vcstools from the data directory.
"""

import os
import re
import glob
import yaml
import psrqpy
import numpy as np

import logging
logger = logging.getLogger(__name__)

# Hard code the path of the flux catalogue directories
CAT_DIR = os.path.join(os.path.dirname(__file__), 'catalogues')

# Grab all the catalogue yamls
CAT_YAMLS = glob.glob("{}/*json".format(CAT_DIR))

# Hard code the path of the ATNF psrcat database file
ATNF_LOC = os.path.join(CAT_DIR, 'psrcat.db')


def get_antf_references():
    ref_dict  = psrqpy.get_references()
    if not isinstance(ref_dict, dict):
        # Reference error so update the cache
        ref_dict  = psrqpy.get_references(updaterefcache=True)
    return ref_dict


def convert_antf_ref(ref_code, ref_dict=None):
    """Converts an ATNF psrcat reference code to a reference in the format "Author Year"

    Parameters
    ----------
    ref_code : `str`
        An ATNF psrcat reference code as found from `psrqpy.get_references(updaterefcache=True)` and https://www.atnf.csiro.au/research/pulsar/psrcat/psrcat_ref.html.
    ref_dict : `dict`, optional
        A previous psrqpy.get_references query. Can be supplied to prevent performing a new query.

    Returns
    -------
    ref : `str`
        Reference in the format "Author Year".
    """
    if ref_dict is None:
        ref_dict = get_antf_references()
    ref_string_list = ref_dict[ref_code].split()

    # Find the parts we need
    author = ref_string_list[0][:-1]
    logger.debug(ref_string_list)
    for ref_part in ref_string_list:
        if ref_part.endswith('.') and len(ref_part) == 5 and ref_part[:-1].isnumeric():
            year = ref_part[:-1]
        elif ref_part.endswith('.') and len(ref_part) == 6 and ref_part[:-2].isnumeric():
            year = ref_part[:-2]
    return f"{author}_{year}"


def flux_from_atnf(pulsar, query=None, ref_dict=None, assumed_error=0.5):
    """Queries the ATNF database for flux and spectral index info on a particular pulsar at all frequencies

    Parameters
    ----------
    pulsar : `str`
        The Jname of the pulsar.
    query : psrqpy object, optional
        A previous psrqpy.QueryATNF query. Can be supplied to prevent performing a new query.
    ref_dict : `dict`, optional
        A previous psrqpy.get_references query. Can be supplied to prevent performing a new query.
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
    # Handle psrqpy queries if None were given
    if query is None:
        query = psrqpy.QueryATNF(psrs=[pulsar], loadfromdb=ATNF_LOC).pandas
    if ref_dict is None:
        ref_dict = get_antf_references()
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
            flux_error_found = True
            try:
                flux_err = query[flux_query+"_ERR"][query_id]
                if flux_err == 0.0:
                    flux_error_found = False
            except KeyError:
                flux_error_found = False
            if np.isnan(flux_err):
                flux_error_found = False
            if not flux_error_found:
                logger.debug("{0} flux error for query: {1}, is zero. Assuming {2:.1f}% uncertainty"\
                                .format(pulsar, flux_query, assumed_error*100))
                flux_err = flux*assumed_error
            flux_err_all.append(flux_err) # in mJy

            # Converts key to frequency in MHz
            if flux_query.endswith("G"):
                # In GHz to convert to MHz
                freq = int(flux_query[1:-1])*1e3
            else:
                freq = int(flux_query[1:])
            freq_all.append(freq) 

            # Grab reference code and convert to "Author Year" format
            ref_code = query[flux_query+"_REF"][query_id]
            ref = convert_antf_ref(ref_code, ref_dict=ref_dict)
            references.append(ref)

    return freq_all, flux_all, flux_err_all, references

def all_flux_from_atnf(query=None):
    if query is None:
        query = psrqpy.QueryATNF(loadfromdb=ATNF_LOC).pandas
    ref_dict = get_antf_references()
    jnames = list(query['PSRJ'])
    jname_cat = {}
    for jname in jnames:
        jname_cat[jname] = {}
        freq_all, flux_all, flux_err_all, references = flux_from_atnf(jname, query=query, ref_dict=ref_dict)
        for freq, flux, flux_err, ref in zip(freq_all, flux_all, flux_err_all, references):
            if ref not in jname_cat[jname].keys():
                jname_cat[jname][ref] = {"Frequency MHz":[], "Flux Density mJy":[], "Flux Density error mJy":[]}
            jname_cat[jname][ref]['Frequency MHz'] += [freq]
            jname_cat[jname][ref]['Flux Density mJy'] += [flux]
            jname_cat[jname][ref]['Flux Density error mJy'] += [flux_err]
    return jname_cat
    

def collect_catalogue_fluxes(only_use=None, exclude=None):
    """Collect the fluxes from all of the catalogues recorded in this repo.

    Parameters
    ----------
    only_use : `list`, optional
        A list of reference labels (in the format 'Author_year') of all the papers you want to use.
    exclude : `list`, optional
        A list of reference labels (in the format 'Author_year') of all the papers you want to exclude.

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
    query = psrqpy.QueryATNF(loadfromdb=ATNF_LOC).pandas
    jnames = list(query['PSRJ'])
    jname_cat_dict = {}
    jname_cat_list = {}
    for jname in jnames:
        jname_cat_dict[jname] = {}
        # freq, flux, flux_err, references
        jname_cat_list[jname] = [[],[],[],[]]

    # Work out which yamls/catalogues to use
    if only_use is None:
        # Use all yamls
        yamls_to_use = CAT_YAMLS
    else:
        yamls_to_use = []
        for yaml_label in only_use:
            y_dir = f"{CAT_DIR}/{yaml_label}.json"
            if os.path.isfile(y_dir):
                yamls_to_use.append(y_dir)
            else:
                logger.warning(f"{yaml_label} not found in {CAT_DIR}")

    # Work out which yamls/catalogues to exclude
    if exclude is not None:
        yamls_to_check = yamls_to_use
        yamls_to_use = []
        for y_dir in yamls_to_check:
            yaml_label = y_dir.split("/")[-1].split(".")[0]
            if yaml_label not in exclude:
                yamls_to_use.append(y_dir)

    # Loop over catalogues and put them into a dictionary
    for cat_file in yamls_to_use:
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

    # Add the antf to the cataogues
    antf_dict = all_flux_from_atnf(query=query)
    for jname in jnames:
        for ref in antf_dict[jname].keys():
            # Check if only_use or exclude allow this ref
            if only_use is not None:
                if ref not in only_use:
                    # Not in only_use so skip
                    continue
            if exclude is not None:
                if ref in exclude:
                    # exclude by skipping
                    continue

            if ref in jname_cat_dict[jname].keys():
                # Check for redundant data
                for freq, flux, flux_err in zip(antf_dict[jname][ref]['Frequency MHz'],
                                                antf_dict[jname][ref]['Flux Density mJy'],
                                                antf_dict[jname][ref]['Flux Density error mJy']):
                    if flux     in jname_cat_dict[jname][ref]['Flux Density mJy'] and \
                       flux_err in jname_cat_dict[jname][ref]['Flux Density error mJy']:
                        logger.debug(f"Redundant data  pulsar:{jname}  ref:{ref}  freq:{freq}  flux:{flux}  flux_err:{flux_err}")
                    else:
                        # Update dict
                        jname_cat_dict[jname][ref]['Frequency MHz'] += [freq]
                        jname_cat_dict[jname][ref]['Flux Density mJy'] += [flux]
                        jname_cat_dict[jname][ref]['Flux Density error mJy'] += [flux_err]
                        # Update list
                        jname_cat_list[jname][0] += [freq]
                        jname_cat_list[jname][1] += [flux]
                        jname_cat_list[jname][2] += [flux_err]
                        jname_cat_list[jname][3] += [ref]
            else:
                # Update dict
                jname_cat_dict[jname][ref] = antf_dict[jname][ref]
                # Update list
                for freq, flux, flux_err in zip(antf_dict[jname][ref]['Frequency MHz'],
                                                antf_dict[jname][ref]['Flux Density mJy'],
                                                antf_dict[jname][ref]['Flux Density error mJy']):
                    jname_cat_list[jname][0] += [freq]
                    jname_cat_list[jname][1] += [flux]
                    jname_cat_list[jname][2] += [flux_err]
                    jname_cat_list[jname][3] += [ref]


    return jname_cat_dict, jname_cat_list

            