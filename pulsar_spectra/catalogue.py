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
CAT_DIR = os.path.join(os.path.dirname(__file__), 'catalogue_papers')

# Grab all the catalogue yamls
CAT_YAMLS = glob.glob("{}/*yaml".format(CAT_DIR))

# ANTF version to be used with all psrqpy querys
ATNF_VER = '1.68'

# dictionary of ADS links
ADS_REF = {
    "Sieber_1973": "https://ui.adsabs.harvard.edu/abs/1973A%26A....28..237S/abstract",
    "Bartel_1978": "https://ui.adsabs.harvard.edu/abs/1978A%26A....68..361B/abstract",
    "Izvekova_1981": "https://ui.adsabs.harvard.edu/abs/1981Ap%26SS..78...45I/abstract",
    "Lorimer_1995": "https://ui.adsabs.harvard.edu/abs/1995ApJ...439..933L/abstract",
    "van_Ommen_1997": "https://ui.adsabs.harvard.edu/abs/1997MNRAS.287..307V/abstract",
    "Maron_2000": "https://ui.adsabs.harvard.edu/abs/2000A%26AS..147..195M/abstract",
    "Malofeev_2000": "https://ui.adsabs.harvard.edu/abs/2000ARep...44..436M/abstract",
    "Karastergiou_2005": "https://ui.adsabs.harvard.edu/abs/2005MNRAS.359..481K/abstract",
    "Johnston_2006": "https://ui.adsabs.harvard.edu/abs/2006MNRAS.369.1916J/abstract",
    "Kijak_2007": "https://ui.adsabs.harvard.edu/abs/2007A%26A...462..699K/abstract",
    "Keith_2011": "https://ui.adsabs.harvard.edu/abs/2011MNRAS.416..346K/abstract",
    "Bates_2011": "https://ui.adsabs.harvard.edu/abs/2011MNRAS.411.1575B/abstract",
    "Kijak_2011": "https://ui.adsabs.harvard.edu/abs/2011A%26A...531A..16K/abstract",
    "Zakharenko_2013": "https://ui.adsabs.harvard.edu/abs/2013MNRAS.431.3624Z/abstract",
    "Dai_2015": "https://ui.adsabs.harvard.edu/abs/2015MNRAS.449.3223D/abstract",
    "Basu_2016": "https://ui.adsabs.harvard.edu/abs/2016MNRAS.458.2509B/abstract",
    "Bell_2016": "https://ui.adsabs.harvard.edu/abs/2016MNRAS.461..908B/abstract",
    "Bilous_2016": "https://ui.adsabs.harvard.edu/abs/2016A%26A...591A.134B/abstract",
    "Han_2016": "https://ui.adsabs.harvard.edu/abs/2016RAA....16..159H/abstract",
    "Murphy_2017": "https://ui.adsabs.harvard.edu/abs/2017PASA...34...20M/abstract",
    "Kijak_2017": "https://ui.adsabs.harvard.edu/abs/2017ApJ...840..108K/abstract",
    "Hobbs_2004a": "https://ui.adsabs.harvard.edu/abs/2004MNRAS.352.1439H/abstract",
    "Johnston_1993": "https://ui.adsabs.harvard.edu/abs/1993Natur.361..613J/abstract",
    "Stovall_2015": "https://ui.adsabs.harvard.edu/abs/2015ApJ...808..156S/abstract",
    "Xue_2017": "https://ui.adsabs.harvard.edu/abs/2017PASA...34...70X/abstract",
    "Jankowski_2018": "https://ui.adsabs.harvard.edu/abs/2018MNRAS.473.4436J/abstract",
    "Bondonneau_2020": "https://ui.adsabs.harvard.edu/abs/2020A%26A...635A..76B/abstract",
    "Johnston_2021": "https://ui.adsabs.harvard.edu/abs/2021MNRAS.502.1253J/abstract",
    "Taylor_1993": "https://ui.adsabs.harvard.edu/abs/1993ApJS...88..529T/abstract",
    "Mignani_2017": "https://ui.adsabs.harvard.edu/abs/2017ApJ...851L..10M/abstract",
    "Johnston_2018": "https://ui.adsabs.harvard.edu/abs/2018MNRAS.474.4629J/abstract",
    "Jankowski_2019": "https://ui.adsabs.harvard.edu/abs/2019MNRAS.484.3691J/abstract",
    "Sanidas_2019": "https://ui.adsabs.harvard.edu/abs/2019A%26A...626A.104S/abstract",
    "Zhao_2019": "https://ui.adsabs.harvard.edu/abs/2019ApJ...874...64Z/abstract",
    "Bilous_2020": "https://ui.adsabs.harvard.edu/abs/2020A%26A...635A..75B/abstract",
    "Stappers_2008" :"https://ui.adsabs.harvard.edu/abs/2008AIPC..983..593S/abstract",
    "McEwen_2020": "https://ui.adsabs.harvard.edu/abs/2020ApJ...892...76M/abstract",
    "Lorimer_2006": "https://ui.adsabs.harvard.edu/abs/2006MNRAS.372..777L/abstract",
    "Kramer_2003a": "https://ui.adsabs.harvard.edu/abs/2003MNRAS.342.1299K/abstract",
    "Han_2021" : "https://ui.adsabs.harvard.edu/abs/2021RAA....21..107H/abstract",
    "Dembska_2014": "https://ui.adsabs.harvard.edu/abs/2014MNRAS.445.3105D/abstract",
    "Camilo_1995": "https://ui.adsabs.harvard.edu/abs/1995ApJ...445..756C/abstract",
    "Robinson_1995": "https://ui.adsabs.harvard.edu/abs/1995MNRAS.274..547R/abstract",
    "McConnell_1991": "https://ui.adsabs.harvard.edu/abs/1991MNRAS.249..654M/abstract",
    "Manchester_1996": "https://ui.adsabs.harvard.edu/abs/1996MNRAS.279.1235M/abstract",
    "Qiao_1995": "https://ui.adsabs.harvard.edu/abs/1995MNRAS.274..572Q/abstract",
    "Manchester_1993": "https://ui.adsabs.harvard.edu/abs/1993ApJ...403L..29M/abstract",
    "Zepka_1996": "https://ui.adsabs.harvard.edu/abs/1996ApJ...456..305Z/abstract",
    "Manchester_1978a": "https://ui.adsabs.harvard.edu/abs/1978MNRAS.185..409M/abstract",
    "Lundgren_1995": "https://ui.adsabs.harvard.edu/abs/1995ApJ...453..419L/abstract",
    "Dewey_1985": "https://ui.adsabs.harvard.edu/abs/1985ApJ...294L..25D/abstract",
    "Nicastro_1995": "https://ui.adsabs.harvard.edu/abs/1995MNRAS.273L..68N/abstract",
    "Johnston_1992": "https://ui.adsabs.harvard.edu/abs/1992MNRAS.255..401J/abstract",
    "Wolszczan_1992": "https://ui.adsabs.harvard.edu/abs/1992Natur.355..145W/abstract",
    "Xie_2019": "https://ui.adsabs.harvard.edu/abs/2019RAA....19..103X/abstract",
    "Lorimer_1995b": "https://ui.adsabs.harvard.edu/abs/1995MNRAS.273..411L/abstract",
    "Kaur_2019": "https://ui.adsabs.harvard.edu/abs/2019ApJ...882..133K/abstract",
    "Manchester_2001": "https://ui.adsabs.harvard.edu/abs/2001MNRAS.328...17M/abstract",
    "Morris_2002": "https://ui.adsabs.harvard.edu/abs/2002MNRAS.335..275M/abstract",
    "Kondratiev_2016": "https://ui.adsabs.harvard.edu/abs/2016A%26A...585A.128K/abstract",
    "Kravtsov_2022": "https://ui.adsabs.harvard.edu/abs/2022MNRAS.512.4324K/abstract",
    "Toscano_1998": "https://ui.adsabs.harvard.edu/abs/1998ApJ...506..863T/abstract",
    "Kuzmin_2001": "https://ui.adsabs.harvard.edu/abs/2001A%26A...368..230K/abstract",
    "Stairs_1999": "https://ui.adsabs.harvard.edu/abs/1999ApJS..123..627S/abstract",
    "Spiewak_2022": "https://ui.adsabs.harvard.edu/abs/2022PASA...39...27S/abstract",
    "Zhang_2019": "https://ui.adsabs.harvard.edu/abs/2019ApJ...885L..37Z/abstract",
    "Lommen_2000": "https://ui.adsabs.harvard.edu/abs/2000ApJ...545.1007L/abstract",
    "Alam_2021": "https://ui.adsabs.harvard.edu/abs/2021ApJS..252....4A/abstract",
    "Bondonneau_2021": "https://ui.adsabs.harvard.edu/abs/2021A%26A...652A..34B/abstract",
    "Kramer_1998": "https://ui.adsabs.harvard.edu/abs/1998ApJ...501..270K/abstract",
    "Kramer_1999": "https://ui.adsabs.harvard.edu/abs/1999ApJ...526..957K/abstract",
    "Frail_2016": "https://ui.adsabs.harvard.edu/abs/2016ApJ...829..119F/abstract",
    "Lee_2022": "https://ui.adsabs.harvard.edu/abs/2022PASA...39...42L/abstract",
    "Bhat_2023": "https://ui.adsabs.harvard.edu/abs/2023arXiv230211920B/abstract",
    "Aloisi_2019":"https://ui.adsabs.harvard.edu/abs/2019ApJ...875...19A/abstract",
    "Bailes_1997":"https://ui.adsabs.harvard.edu/abs/1997ApJ...481..386B/abstract",
    "Basu_2018":"https://ui.adsabs.harvard.edu/abs/2018MNRAS.475.1469B/abstract",
    "Biggs_1996":"https://ui.adsabs.harvard.edu/abs/1996MNRAS.282..691B/abstract",
    "Boyles_2013":"https://ui.adsabs.harvard.edu/abs/2013ApJ...763...80B/abstract",
    "Brinkman_2018":"https://ui.adsabs.harvard.edu/abs/2018MNRAS.474.2012B",
    "Champion_2005a":"https://ui.adsabs.harvard.edu/abs/2005MNRAS.363..929C",
    "Champion_2005b":"https://ui.adsabs.harvard.edu/abs/2005PhDT.......282C",
    "Crawford_2001":"https://ui.adsabs.harvard.edu/abs/2001AJ....122.2001C/abstract",
    "Crawford_2007":"https://ui.adsabs.harvard.edu/abs/2007AJ....134.1231C/abstract",
    "Deller_2009":"https://ui.adsabs.harvard.edu/abs/2009ApJ...701.1243D/abstract",
    "Dembska_2015":"https://ui.adsabs.harvard.edu/abs/2015MNRAS.449.1869D",
    "Demorest_2013":"https://ui.adsabs.harvard.edu/abs/2013ApJ...762...94D",
    "Esamdin_2004":"https://ui.adsabs.harvard.edu/abs/2004A&A...425..949E",
    "Freire_2007":"https://ui.adsabs.harvard.edu/abs/2007ApJ...662.1177F",
    "Gentile_2018":"https://ui.adsabs.harvard.edu/abs/2018ApJ...868..122B",
    "Giacani_2001":"https://ui.adsabs.harvard.edu/abs/2001AJ....121.3133G",
    "Han_1999":"https://ui.adsabs.harvard.edu/abs/1999A&AS..136..571H",
    "Hoensbroech_1997":"https://ui.adsabs.harvard.edu/abs/1997A%26AS..126..121V/abstract",
    "Joshi_2009":"https://ui.adsabs.harvard.edu/abs/2009MNRAS.398..943J/abstract",
    "Kaspi_1997":"https://ui.adsabs.harvard.edu/abs/1997ApJ...485..820K",
    "Kijak_1998":"https://ui.adsabs.harvard.edu/abs/1998A%26AS..127..153K/abstract",
    "Kramer_1997":"https://ui.adsabs.harvard.edu/abs/1997ApJ...488..364K",
    "Kuniyoshi_2015":"https://ui.adsabs.harvard.edu/abs/2015MNRAS.453..828K/abstract",
    "Lewandowski_2004":"https://ui.adsabs.harvard.edu/abs/2004ApJ...600..905L",
    "Lorimer_1995":"https://ui.adsabs.harvard.edu/abs/1995ApJ...439..933L",
    "Lorimer_1996":"https://ui.adsabs.harvard.edu/abs/1996MNRAS.283.1383L",
    "Lorimer_2005":"https://ui.adsabs.harvard.edu/abs/2005MNRAS.359.1524L",
    "Lorimer_2007":"https://ui.adsabs.harvard.edu/abs/2007MNRAS.379..282L",
    "Lynch_2012":"https://ui.adsabs.harvard.edu/abs/2012ApJ...745..109L",
    "Lynch_2013":"https://ui.adsabs.harvard.edu/abs/2013ApJ...763...81L/abstract",
    "Manchester_1995":"https://ui.adsabs.harvard.edu/abs/1995ApJ...441L..65M/abstract",
    "Manchester_2013":"https://ui.adsabs.harvard.edu/abs/2013PASA...30...17M/abstract",
    "Michilli_2020":"https://ui.adsabs.harvard.edu/abs/2020MNRAS.491..725M/abstract",
    "Mickaliger_2012":"https://ui.adsabs.harvard.edu/abs/2012ApJ...759..127M",
    "Mikhailov_2016":"https://ui.adsabs.harvard.edu/abs/2016A%26A...593A..21M/abstract",
    "Ng_2015":"https://ui.adsabs.harvard.edu/abs/2015MNRAS.450.2922N",
    "RoZko_2018":"https://ui.adsabs.harvard.edu/abs/2018MNRAS.479.2193R",
    "Sayer_1997":"https://ui.adsabs.harvard.edu/abs/1997ApJ...474..426S",
    "Seiradakis_1995":"https://ui.adsabs.harvard.edu/abs/1995A%26AS..111..205S/abstract",
    "Shapiro_Albert_2021":"https://ui.adsabs.harvard.edu/abs/2021ApJ...909..219S",
    "Stovall_2014":"https://ui.adsabs.harvard.edu/abs/2014ApJ...791...67S/abstract",
    "Surnis_2019":"https://ui.adsabs.harvard.edu/abs/2019ApJ...870....8S/abstract",
    "Titus_2019":"https://ui.adsabs.harvard.edu/abs/2019MNRAS.487.4332T",
    "Zhao_2017":"https://ui.adsabs.harvard.edu/abs/2017ApJ...845..156Z/abstract",
    "Gitika_2023":"https://ui.adsabs.harvard.edu/abs/2023MNRAS.526.3370G/abstract",
    "Crowter_2020":"https://ui.adsabs.harvard.edu/abs/2020MNRAS.495.3052C/abstract",
    "Janssen_2009":"https://ui.adsabs.harvard.edu/abs/2009A%26A...498..223J/abstract",
    "Weisberg_1999":"https://ui.adsabs.harvard.edu/abs/1999ApJS..121..171W/abstract",
    "Stokes_1985":"https://ui.adsabs.harvard.edu/abs/1985Natur.317..787S/abstract",
    "Stokes_1986":"https://ui.adsabs.harvard.edu/abs/1986ApJ...311..694S/abstract",
    "Tan_2020":"https://ui.adsabs.harvard.edu/abs/2020MNRAS.492.5878T/abstract",
    "Ng_2015":"https://ui.adsabs.harvard.edu/abs/2015MNRAS.450.2922N/abstract",
    "McLean_1973":"https://ui.adsabs.harvard.edu/abs/1973MNRAS.165..133M/abstract",
    "McGary_2001":"https://ui.adsabs.harvard.edu/abs/2001AJ....121.1192M/abstract",
    "Lazarus_2015":"https://ui.adsabs.harvard.edu/abs/2015ApJ...812...81L/abstract",
    "Curylo_2020":"https://ui.adsabs.harvard.edu/abs/2020MNRAS.495.3052C/abstract",
    "Shrauner_1998":"https://ui.adsabs.harvard.edu/abs/1998ApJ...509..785S/abstract",
    "Foster_1991":"https://ui.adsabs.harvard.edu/abs/1991ApJ...378..687F/abstract",
    "Bhattacharyya_2016":"https://ui.adsabs.harvard.edu/abs/2016ApJ...817..130B/abstract",
    "Kouwenhoven_2000":"https://ui.adsabs.harvard.edu/abs/2000A%26AS..145..243K/abstract",
    "Dowell_2013":"https://ui.adsabs.harvard.edu/abs/2013ApJ...775L..28D/abstract",
    "Deneva_2016":"https://ui.adsabs.harvard.edu/abs/2016ApJ...821...10D/abstract",
    "Malofeev_1993":"https://ui.adsabs.harvard.edu/abs/1993AstL...19..138M/abstract",
}


def get_antf_references():
    """Wrapper for psrqpy.get_references() that ensures the cache is only Updated once."""
    ref_dict  = psrqpy.get_references(version=ATNF_VER)
    if not isinstance(ref_dict, dict):
        # Reference error so update the cache
        ref_dict  = psrqpy.get_references(version=ATNF_VER, updaterefcache=True)
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
    try:
        ref_string_list = ref_dict[ref_code].split()
    except KeyError or TypeError:
        # If the psrcat database file is changed this will update the ref_code
        logger.debug(ref_dict)
        psrqpy.QueryATNF(version=ATNF_VER, checkupdate=True)
        ref_dict = get_antf_references()
        logger.debug(ref_dict)
        ref_string_list = ref_dict[ref_code].split()

    # Find the parts we need
    author = ref_string_list[0][:-1]
    #logger.debug(ref_string_list)
    for ref_part in ref_string_list:
        if ref_part.endswith('.') and len(ref_part) == 5 and ref_part[:-1].isnumeric():
            year = ref_part[:-1]
        elif ref_part.endswith('.') and len(ref_part) == 6 and ref_part[:-2].isnumeric():
            year = ref_part[:-1]
    return f"{author}_{year}"


def flux_from_atnf(pulsar, query=None, ref_dict=None, assumed_error=0.5):
    """Queries the ATNF database for flux info on a particular pulsar at all frequencies.

    Parameters
    ----------
    pulsar : `str`
        The Jname of the pulsar.
    query : psrqpy object, optional
        A previous psrqpy.QueryATNF query. Can be supplied to prevent performing a new query.
    ref_dict : `dict`, optional
        A previous psrqpy.get_references query. Can be supplied to prevent performing a new query.
    assumed_error : `float`, optional
        If no error found, apply this factor to flux to make an assumed error. |br| Default: 0.5.

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
        query = psrqpy.QueryATNF(version=ATNF_VER, psrs=[pulsar]).pandas
    if ref_dict is None:
        ref_dict = get_antf_references()
    query_id = list(query['PSRJ']).index(pulsar)

    # Find all flux queries from keys
    flux_queries = []
    for table_param in query.keys():
        if re.match("S\d*\d$", table_param) or re.match("S\d*G$", table_param):
            flux_queries.append(table_param)

    freq_all     = []
    band_all     = []
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
            band_all.append(None)

            # Grab reference code and convert to "Author Year" format
            ref_code = query[flux_query+"_REF"][query_id]
            ref = convert_antf_ref(ref_code, ref_dict=ref_dict)
            references.append(f"{ref}_ATNF")

    return freq_all, band_all, flux_all, flux_err_all, references

def all_flux_from_atnf(query=None):
    """Queries the ATNF database for flux info for all pulsar at all frequencies.

    Parameters
    ----------
    query : psrqpy object, optional
        A previous psrqpy.QueryATNF query. Can be supplied to prevent performing a new query.

    Returns
    -------
    jname_cat_dict : `dict`
        Catalgoues dictionary with the keys in the format jname_cat_dict[jname][ref]['Frequency MHz', 'Flux Density mJy', 'Flux Density error mJy']

        ``'jname'`` : `str`
            The pulsar's Jname.
        ``'ref'`` : `str`
            The reference label.
        ``'Frequency MHz'``
            The observing frequency in MHz.
        ``'Flux Density mJy'``
            The flux density in mJy.
        ``'Flux Density error mJy'``
            The error of the flux density in mJy.
    """
    if query is None:
        query = psrqpy.QueryATNF(version=ATNF_VER).pandas
    ref_dict = get_antf_references()
    jnames = list(query['PSRJ'])
    jname_cat = {}
    for jname in jnames:
        jname_cat[jname] = {}
        freq_all, band_all, flux_all, flux_err_all, references = flux_from_atnf(jname, query=query, ref_dict=ref_dict)
        for freq, band, flux, flux_err, ref in zip(freq_all, band_all, flux_all, flux_err_all, references):
            if ref not in jname_cat[jname].keys():
                jname_cat[jname][ref] = {
                    "Frequency MHz":[],
                    "Bandwidth MHz":[],
                    "Flux Density mJy":[],
                    "Flux Density error mJy":[],
                }
            jname_cat[jname][ref]['Frequency MHz'] += [freq]
            # Add Nones so the software can easily tell there are missing bandwidths
            jname_cat[jname][ref]['Bandwidth MHz'] += [band]
            jname_cat[jname][ref]['Flux Density mJy'] += [flux]
            jname_cat[jname][ref]['Flux Density error mJy'] += [flux_err]
    return jname_cat


def collect_catalogue_fluxes(only_use=None, exclude=None, query=None, use_atnf=True):
    """Collect the fluxes from all of the catalogues recorded in this repo.

    Parameters
    ----------
    only_use : `list`, optional
        A list of reference labels (in the format 'Author_year') of all the papers you want to use.
    exclude : `list`, optional
        A list of reference labels (in the format 'Author_year') of all the papers you want to exclude.
    query : psrqpy object, optional
        A previous psrqpy.QueryATNF query. Can be supplied to prevent performing a new query.
    use_atnf: `bool`, optional
        Whether the ATNF values should be included. Default: True.

    Returns
    -------
    jname_cat_list[jname] : `dict`
        Catalgoues dictionary with the keys:

        ``'jname'`` : `str`
            The pulsar's Jname.

            Each dictionary contains a list of lists with the following:

            Frequency MHz : `list`
                The observing frequency in MHz.
            Flux Density mJy : `list`
                The flux density in mJy.
            Flux Density error mJy : `list`
                The error of the flux density in mJy.
            ref : `list`
                The reference label (in the format 'Author_year').
    """
    if query is None:
        query = psrqpy.QueryATNF(version=ATNF_VER).pandas
    # Make a dictionary for each pulsar
    jnames = list(query['PSRJ'])
    jname_cat_dict = {}
    jname_cat_list = {}
    for jname in jnames:
        jname_cat_dict[jname] = {}
        # freq, flux, flux_err, references
        jname_cat_list[jname] = [[],[],[],[],[]]

    # Work out which yamls/catalogues to use
    if only_use is None:
        # Use all yamls
        yamls_to_use = CAT_YAMLS
    else:
        yamls_to_use = []
        for yaml_label in only_use:
            y_dir = f"{CAT_DIR}/{yaml_label}.yaml"
            if os.path.isfile(y_dir):
                yamls_to_use.append(y_dir)
            else:
                logger.warning(f"{yaml_label} not found in {CAT_DIR}")

    # Work out which yamls/catalogues to exclude
    if exclude is not None:
        yamls_to_check = yamls_to_use
        yamls_to_use = []
        for y_dir in yamls_to_check:
            yaml_label = os.path.basename(y_dir).split(".")[0]
            if yaml_label not in exclude:
                yamls_to_use.append(y_dir)

    # Loop over catalogues and put them into a dictionary
    yamls_to_use.sort()
    for cat_file in yamls_to_use:
        cat_label = os.path.basename(cat_file).split(".")[0]

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
                jname_cat_list[jname][1] += cat_dict[jname]['Bandwidth MHz']
                jname_cat_list[jname][2] += cat_dict[jname]['Flux Density mJy']
                jname_cat_list[jname][3] += cat_dict[jname]['Flux Density error mJy']
                jname_cat_list[jname][4] += [cat_label] * len(cat_dict[jname]['Frequency MHz'])

    if not use_atnf:
        # return before including atnf
        return jname_cat_list

    # Add the antf to the cataogues
    antf_dict = all_flux_from_atnf(query=query)
    # refs that have errors that we plan to inform ATNF about
    antf_incorrect_refs = ["Zhao_2019", "Mignani_2017", "Bell_2016", "Robinson_1995", "Johnston_1994", "Manchester_1996", "Xie_2019", "Han_2016", "Kramer_1999", "Kondratiev_2015", "Crawford_2001", "Michilli_2020", "Manchester_2013", "Brinkman_2018"]
    # refs that are correct but where scaled to by their spectral index for the ATNF frequencies
    antf_adjusted_refs = ["Lorimer_1995b", "Stovall_2015", "Sanidas_2019", "Wolszczan_1992", "Dembska_2014", "Kaur_2019", "Alam_2021", "Foster_1991"]
    # refs that were rounded to different decimal places than the publications
    antf_rounded_refs = ["Johnston_2018", "Dai_2015", "McEwen_2020", "McConnell_1991", "Bondonneau_2020", "Johnston_2021", "Bates_2011", "Han_2021", "Sayer_1997", "Lynch_2012", "Stovall_2014", "Crowter_2020"]
    # refs that have different uncertainties than published
    antf_uncert_refs = ["Stairs_1999", "Kuzmin_2001", "Jankowski_2019", "Jankowski_2018", "Kramer_2003a", "Manchester_2001", "Morris_2002", "Zhang_2019"]
    for jname in jnames:
        for ref in antf_dict[jname].keys():
            # Remove "_antf" from the end of  the reference
            raw_ref = ref[:-5]
            # Check if only_use or exclude allow this ref
            if only_use is not None:
                if raw_ref not in only_use:
                    # Not in only_use so skip
                    continue
            if exclude is None:
                exclude = []
            if raw_ref in exclude + antf_incorrect_refs + antf_adjusted_refs + antf_rounded_refs + antf_uncert_refs:
                # exclude by skipping
                continue

            if raw_ref in jname_cat_dict[jname].keys():
                # Check for redundant data
                for freq, band, flux, flux_err in zip(antf_dict[jname][ref]['Frequency MHz'],
                                                      antf_dict[jname][ref]['Bandwidth MHz'],
                                                      antf_dict[jname][ref]['Flux Density mJy'],
                                                      antf_dict[jname][ref]['Flux Density error mJy']):
                    if flux     in jname_cat_dict[jname][raw_ref]['Flux Density mJy'] and \
                       flux_err in jname_cat_dict[jname][raw_ref]['Flux Density error mJy']:
                        logger.debug(f"Redundant data  pulsar:{jname}  ref:{raw_ref}  freq:{freq}  flux:{flux}  flux_err:{flux_err}")
                    else:
                        # Update list
                        jname_cat_list[jname][0] += [freq]
                        jname_cat_list[jname][1] += [band]
                        jname_cat_list[jname][2] += [flux]
                        jname_cat_list[jname][3] += [flux_err]
                        jname_cat_list[jname][4] += [ref]
            else:
                # Update list
                for freq, band, flux, flux_err in zip(antf_dict[jname][ref]['Frequency MHz'],
                                                      antf_dict[jname][ref]['Bandwidth MHz'],
                                                      antf_dict[jname][ref]['Flux Density mJy'],
                                                      antf_dict[jname][ref]['Flux Density error mJy']):
                    jname_cat_list[jname][0] += [freq]
                    jname_cat_list[jname][1] += [band]
                    jname_cat_list[jname][2] += [flux]
                    jname_cat_list[jname][3] += [flux_err]
                    jname_cat_list[jname][4] += [ref]

    return jname_cat_list

def convert_cat_list_to_dict(jname_cat_list):
    """
    Returns
    -------
    jname_cat_dict : `dict`
        Catalgoues dictionary with the keys in the format jname_cat_dict[jname][ref]['Frequency MHz', 'Flux Density mJy', 'Flux Density error mJy']

        ``'jname'`` : `str`
            The pulsar's Jname.
        ``'ref'`` : `str`
            The reference label.
        ``'Frequency MHz'``
            The observing frequency in MHz.
        ``'Flux Density mJy'``
            The flux density in mJy.
        ``'Flux Density error mJy'``
            The error of the flux density in mJy.
    """
    jname_cat_dict = {}
    for jname in jname_cat_list.keys():
        freqs, bands, fluxs, flux_errs, refs = jname_cat_list[jname]
        jname_cat_dict[jname] = {}

        # Loop over and put references into the same dict
        for freq, band, flux, flux_err, ref in zip(freqs, bands, fluxs, flux_errs, refs):
            if ref in jname_cat_dict[jname].keys():
                # Update
                jname_cat_dict[jname][ref]['Frequency MHz'] += [freq]
                jname_cat_dict[jname][ref]['Bandwidth MHz'] += [band]
                jname_cat_dict[jname][ref]['Flux Density mJy'] += [flux]
                jname_cat_dict[jname][ref]['Flux Density error mJy'] += [flux_err]
            else:
                # Make new
                jname_cat_dict[jname][ref] = {}
                jname_cat_dict[jname][ref]['Frequency MHz'] = [freq]
                jname_cat_dict[jname][ref]['Bandwidth MHz'] = [band]
                jname_cat_dict[jname][ref]['Flux Density mJy'] = [flux]
                jname_cat_dict[jname][ref]['Flux Density error mJy'] = [flux_err]
    return jname_cat_dict
