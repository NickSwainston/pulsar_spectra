"""
Loads all the data required by vcstools from the data directory.
"""

import glob
import logging
import os
import re

import numpy as np
import psrqpy
import yaml

logger = logging.getLogger(__name__)

# Hard code the path of the flux catalogue directories
CAT_DIR = os.path.join(os.path.dirname(__file__), "catalogue_papers")

# Grab all the catalogue yamls
CAT_YAMLS = glob.glob("{}/*yaml".format(CAT_DIR))

# atnf version to be used with all psrqpy querys
ATNF_VER = "2.6.2"

# dictionary of ADS links
ADS_REF = {
    "Sieber_1973": "https://ui.adsabs.harvard.edu/abs/1973A%26A....28..237S",
    "Bartel_1978": "https://ui.adsabs.harvard.edu/abs/1978A%26A....68..361B",
    "Izvekova_1981": "https://ui.adsabs.harvard.edu/abs/1981Ap%26SS..78...45I",
    "Lorimer_1995": "https://ui.adsabs.harvard.edu/abs/1995ApJ...439..933L",
    "van_Ommen_1997": "https://ui.adsabs.harvard.edu/abs/1997MNRAS.287..307V",
    "Maron_2000": "https://ui.adsabs.harvard.edu/abs/2000A%26AS..147..195M",
    "Malofeev_2000": "https://ui.adsabs.harvard.edu/abs/2000ARep...44..436M",
    "Karastergiou_2005": "https://ui.adsabs.harvard.edu/abs/2005MNRAS.359..481K",
    "Johnston_2006": "https://ui.adsabs.harvard.edu/abs/2006MNRAS.369.1916J",
    "Kijak_2007": "https://ui.adsabs.harvard.edu/abs/2007A%26A...462..699K",
    "Keith_2011": "https://ui.adsabs.harvard.edu/abs/2011MNRAS.416..346K",
    "Bates_2011": "https://ui.adsabs.harvard.edu/abs/2011MNRAS.411.1575B",
    "Kijak_2011": "https://ui.adsabs.harvard.edu/abs/2011A%26A...531A..16K",
    "Zakharenko_2013": "https://ui.adsabs.harvard.edu/abs/2013MNRAS.431.3624Z",
    "Dai_2015": "https://ui.adsabs.harvard.edu/abs/2015MNRAS.449.3223D",
    "Basu_2016": "https://ui.adsabs.harvard.edu/abs/2016MNRAS.458.2509B",
    "Bell_2016": "https://ui.adsabs.harvard.edu/abs/2016MNRAS.461..908B",
    "Bilous_2016": "https://ui.adsabs.harvard.edu/abs/2016A%26A...591A.134B",
    "Han_2016": "https://ui.adsabs.harvard.edu/abs/2016RAA....16..159H",
    "Murphy_2017": "https://ui.adsabs.harvard.edu/abs/2017PASA...34...20M",
    "Kijak_2017": "https://ui.adsabs.harvard.edu/abs/2017ApJ...840..108K",
    "Hobbs_2004a": "https://ui.adsabs.harvard.edu/abs/2004MNRAS.352.1439H",
    "Johnston_1993": "https://ui.adsabs.harvard.edu/abs/1993Natur.361..613J",
    "Stovall_2015": "https://ui.adsabs.harvard.edu/abs/2015ApJ...808..156S",
    "Xue_2017": "https://ui.adsabs.harvard.edu/abs/2017PASA...34...70X",
    "Jankowski_2018": "https://ui.adsabs.harvard.edu/abs/2018MNRAS.473.4436J",
    "Bondonneau_2020": "https://ui.adsabs.harvard.edu/abs/2020A%26A...635A..76B",
    "Johnston_2021": "https://ui.adsabs.harvard.edu/abs/2021MNRAS.502.1253J",
    "Taylor_1993": "https://ui.adsabs.harvard.edu/abs/1993ApJS...88..529T",
    "Mignani_2017": "https://ui.adsabs.harvard.edu/abs/2017ApJ...851L..10M",
    "Johnston_2018": "https://ui.adsabs.harvard.edu/abs/2018MNRAS.474.4629J",
    "Jankowski_2019": "https://ui.adsabs.harvard.edu/abs/2019MNRAS.484.3691J",
    "Sanidas_2019": "https://ui.adsabs.harvard.edu/abs/2019A%26A...626A.104S",
    "Zhao_2019": "https://ui.adsabs.harvard.edu/abs/2019ApJ...874...64Z",
    "Bilous_2020": "https://ui.adsabs.harvard.edu/abs/2020A%26A...635A..75B",
    "Stappers_2008": "https://ui.adsabs.harvard.edu/abs/2008AIPC..983..593S",
    "McEwen_2020": "https://ui.adsabs.harvard.edu/abs/2020ApJ...892...76M",
    "Lorimer_2006": "https://ui.adsabs.harvard.edu/abs/2006MNRAS.372..777L",
    "Kramer_2003a": "https://ui.adsabs.harvard.edu/abs/2003MNRAS.342.1299K",
    "Han_2021": "https://ui.adsabs.harvard.edu/abs/2021RAA....21..107H",
    "Dembska_2014": "https://ui.adsabs.harvard.edu/abs/2014MNRAS.445.3105D",
    "Camilo_1995": "https://ui.adsabs.harvard.edu/abs/1995ApJ...445..756C",
    "Robinson_1995": "https://ui.adsabs.harvard.edu/abs/1995MNRAS.274..547R",
    "McConnell_1991": "https://ui.adsabs.harvard.edu/abs/1991MNRAS.249..654M",
    "Manchester_1996": "https://ui.adsabs.harvard.edu/abs/1996MNRAS.279.1235M",
    "Qiao_1995": "https://ui.adsabs.harvard.edu/abs/1995MNRAS.274..572Q",
    "Manchester_1993": "https://ui.adsabs.harvard.edu/abs/1993ApJ...403L..29M",
    "Zepka_1996": "https://ui.adsabs.harvard.edu/abs/1996ApJ...456..305Z",
    "Manchester_1978a": "https://ui.adsabs.harvard.edu/abs/1978MNRAS.185..409M",
    "Lundgren_1995": "https://ui.adsabs.harvard.edu/abs/1995ApJ...453..419L",
    "Dewey_1985": "https://ui.adsabs.harvard.edu/abs/1985ApJ...294L..25D",
    "Nicastro_1995": "https://ui.adsabs.harvard.edu/abs/1995MNRAS.273L..68N",
    "Johnston_1992": "https://ui.adsabs.harvard.edu/abs/1992MNRAS.255..401J",
    "Wolszczan_1992": "https://ui.adsabs.harvard.edu/abs/1992Natur.355..145W",
    "Xie_2019": "https://ui.adsabs.harvard.edu/abs/2019RAA....19..103X",
    "Lorimer_1995b": "https://ui.adsabs.harvard.edu/abs/1995MNRAS.273..411L",
    "Kaur_2019": "https://ui.adsabs.harvard.edu/abs/2019ApJ...882..133K",
    "Manchester_2001": "https://ui.adsabs.harvard.edu/abs/2001MNRAS.328...17M",
    "Morris_2002": "https://ui.adsabs.harvard.edu/abs/2002MNRAS.335..275M",
    "Kondratiev_2016": "https://ui.adsabs.harvard.edu/abs/2016A%26A...585A.128K",
    "Kravtsov_2022": "https://ui.adsabs.harvard.edu/abs/2022MNRAS.512.4324K",
    "Toscano_1998": "https://ui.adsabs.harvard.edu/abs/1998ApJ...506..863T",
    "Kuzmin_2001": "https://ui.adsabs.harvard.edu/abs/2001A%26A...368..230K",
    "Stairs_1999": "https://ui.adsabs.harvard.edu/abs/1999ApJS..123..627S",
    "Spiewak_2022": "https://ui.adsabs.harvard.edu/abs/2022PASA...39...27S",
    "Zhang_2019": "https://ui.adsabs.harvard.edu/abs/2019ApJ...885L..37Z",
    "Lommen_2000": "https://ui.adsabs.harvard.edu/abs/2000ApJ...545.1007L",
    "Alam_2021": "https://ui.adsabs.harvard.edu/abs/2021ApJS..252....4A",
    "Bondonneau_2021": "https://ui.adsabs.harvard.edu/abs/2021A%26A...652A..34B",
    "Kramer_1998": "https://ui.adsabs.harvard.edu/abs/1998ApJ...501..270K",
    "Kramer_1999": "https://ui.adsabs.harvard.edu/abs/1999ApJ...526..957K",
    "Frail_2016": "https://ui.adsabs.harvard.edu/abs/2016ApJ...829..119F",
    "Lee_2022": "https://ui.adsabs.harvard.edu/abs/2022PASA...39...42L",
    "Bhat_2023": "https://ui.adsabs.harvard.edu/abs/2023PASA...40...20B",
    "Aloisi_2019": "https://ui.adsabs.harvard.edu/abs/2019ApJ...875...19A",
    "Bailes_1997": "https://ui.adsabs.harvard.edu/abs/1997ApJ...481..386B",
    "Basu_2018": "https://ui.adsabs.harvard.edu/abs/2018MNRAS.475.1469B",
    "Biggs_1996": "https://ui.adsabs.harvard.edu/abs/1996MNRAS.282..691B",
    "Boyles_2013": "https://ui.adsabs.harvard.edu/abs/2013ApJ...763...80B",
    "Brinkman_2018": "https://ui.adsabs.harvard.edu/abs/2018MNRAS.474.2012B",
    "Champion_2005a": "https://ui.adsabs.harvard.edu/abs/2005MNRAS.363..929C",
    "Champion_2005b": "https://ui.adsabs.harvard.edu/abs/2005PhDT.......282C",
    "Crawford_2001": "https://ui.adsabs.harvard.edu/abs/2001AJ....122.2001C",
    "Crawford_2007": "https://ui.adsabs.harvard.edu/abs/2007AJ....134.1231C",
    "Deller_2009": "https://ui.adsabs.harvard.edu/abs/2009ApJ...701.1243D",
    "Dembska_2015": "https://ui.adsabs.harvard.edu/abs/2015MNRAS.449.1869D",
    "Demorest_2013": "https://ui.adsabs.harvard.edu/abs/2013ApJ...762...94D",
    "Esamdin_2004": "https://ui.adsabs.harvard.edu/abs/2004A&A...425..949E",
    "Freire_2007": "https://ui.adsabs.harvard.edu/abs/2007ApJ...662.1177F",
    "Gentile_2018": "https://ui.adsabs.harvard.edu/abs/2018ApJ...862...47G",
    "Giacani_2001": "https://ui.adsabs.harvard.edu/abs/2001AJ....121.3133G",
    "Han_1999": "https://ui.adsabs.harvard.edu/abs/1999A&AS..136..571H",
    "Hoensbroech_1997": "https://ui.adsabs.harvard.edu/abs/1997A%26AS..126..121V",
    "Joshi_2009": "https://ui.adsabs.harvard.edu/abs/2009MNRAS.398..943J",
    "Kaspi_1997": "https://ui.adsabs.harvard.edu/abs/1997ApJ...485..820K",
    "Kijak_1997": "https://ui.adsabs.harvard.edu/abs/1997A%26A...318L..63K",
    "Kijak_1998": "https://ui.adsabs.harvard.edu/abs/1998A%26AS..127..153K",
    "Kramer_1997": "https://ui.adsabs.harvard.edu/abs/1997ApJ...488..364K",
    "Kuniyoshi_2015": "https://ui.adsabs.harvard.edu/abs/2015MNRAS.453..828K",
    "Lewandowski_2004": "https://ui.adsabs.harvard.edu/abs/2004ApJ...600..905L",
    "Lorimer_1996": "https://ui.adsabs.harvard.edu/abs/1996MNRAS.283.1383L",
    "Lorimer_2005": "https://ui.adsabs.harvard.edu/abs/2005MNRAS.359.1524L",
    "Lorimer_2007": "https://ui.adsabs.harvard.edu/abs/2007MNRAS.379..282L",
    "Lynch_2012": "https://ui.adsabs.harvard.edu/abs/2012ApJ...745..109L",
    "Lynch_2013": "https://ui.adsabs.harvard.edu/abs/2013ApJ...763...81L",
    "Manchester_1995": "https://ui.adsabs.harvard.edu/abs/1995ApJ...441L..65M",
    "Manchester_2013": "https://ui.adsabs.harvard.edu/abs/2013PASA...30...17M",
    "Michilli_2020": "https://ui.adsabs.harvard.edu/abs/2020MNRAS.491..725M",
    "Mickaliger_2012": "https://ui.adsabs.harvard.edu/abs/2012ApJ...759..127M",
    "Mikhailov_2016": "https://ui.adsabs.harvard.edu/abs/2016A%26A...593A..21M",
    "Ng_2015": "https://ui.adsabs.harvard.edu/abs/2015MNRAS.450.2922N",
    "RoZko_2018": "https://ui.adsabs.harvard.edu/abs/2018MNRAS.479.2193R",
    "Sayer_1997": "https://ui.adsabs.harvard.edu/abs/1997ApJ...474..426S",
    "Seiradakis_1995": "https://ui.adsabs.harvard.edu/abs/1995A%26AS..111..205S",
    "Shapiro_Albert_2021": "https://ui.adsabs.harvard.edu/abs/2021ApJ...909..219S",
    "Stovall_2014": "https://ui.adsabs.harvard.edu/abs/2014ApJ...791...67S",
    "Surnis_2019": "https://ui.adsabs.harvard.edu/abs/2019ApJ...870....8S",
    "Titus_2019": "https://ui.adsabs.harvard.edu/abs/2019MNRAS.487.4332T",
    "Zhao_2017": "https://ui.adsabs.harvard.edu/abs/2017ApJ...845..156Z",
    "Gitika_2023": "https://ui.adsabs.harvard.edu/abs/2023MNRAS.526.3370G",
    "Crowter_2020": "https://ui.adsabs.harvard.edu/abs/2020MNRAS.495.3052C",
    "Janssen_2009": "https://ui.adsabs.harvard.edu/abs/2009A%26A...498..223J",
    "Weisberg_1999": "https://ui.adsabs.harvard.edu/abs/1999ApJS..121..171W",
    "Stokes_1985": "https://ui.adsabs.harvard.edu/abs/1985Natur.317..787S",
    "Stokes_1986": "https://ui.adsabs.harvard.edu/abs/1986ApJ...311..694S",
    "Tan_2020": "https://ui.adsabs.harvard.edu/abs/2020MNRAS.492.5878T",
    "McLean_1973": "https://ui.adsabs.harvard.edu/abs/1973MNRAS.165..133M",
    "McGary_2001": "https://ui.adsabs.harvard.edu/abs/2001AJ....121.1192M",
    "Lazarus_2015": "https://ui.adsabs.harvard.edu/abs/2015ApJ...812...81L",
    "Curylo_2020": "https://ui.adsabs.harvard.edu/abs/2020MNRAS.495.3052C",
    "Shrauner_1998": "https://ui.adsabs.harvard.edu/abs/1998ApJ...509..785S",
    "Foster_1991": "https://ui.adsabs.harvard.edu/abs/1991ApJ...378..687F",
    "Bhattacharyya_2016": "https://ui.adsabs.harvard.edu/abs/2016ApJ...817..130B",
    "Kouwenhoven_2000": "https://ui.adsabs.harvard.edu/abs/2000A%26AS..145..243K",
    "Dowell_2013": "https://ui.adsabs.harvard.edu/abs/2013ApJ...775L..28D",
    "Deneva_2016": "https://ui.adsabs.harvard.edu/abs/2016ApJ...821...10D",
    "Malofeev_1993": "https://ui.adsabs.harvard.edu/abs/1993AstL...19..138M",
    "Slee_1986": "https://ui.adsabs.harvard.edu/abs/1986AuJPh..39..103S",
    "Fruchter_1988": "https://ui.adsabs.harvard.edu/abs/1988Natur.333..237F",
    "Fruchter_1990": "https://ui.adsabs.harvard.edu/abs/1990ApJ...351..642F",
    "Bailes_1994": "https://ui.adsabs.harvard.edu/abs/1994ApJ...425L..41B",
    "Navarro_1995": "https://ui.adsabs.harvard.edu/abs/1995ApJ...455L..55N",
    "Camilo_1996": "https://ui.adsabs.harvard.edu/abs/1996ApJ...469..819C",
    "Maron_2004": "https://ui.adsabs.harvard.edu/abs/2004A%26A...413L..19M",
    "Wielebinski_1993": "https://ui.adsabs.harvard.edu/abs/1993A%26A...272L..13W",
    "Champion_2008": "https://ui.adsabs.harvard.edu/abs/2008Sci...320.1309C",
    "Hessels_2011": "https://ui.adsabs.harvard.edu/abs/2011AIPC.1357...40H",
    "Kowalinska_2012": "https://ui.adsabs.harvard.edu/abs/2012ASPC..466..101K",
    "Levin_2016": "https://ui.adsabs.harvard.edu/abs/2016ApJ...818..166L",
    "Wang_2024": "https://ui.adsabs.harvard.edu/abs/2024ApJ...961...48W",
    "Keith_2024": "https://ui.adsabs.harvard.edu/abs/2024MNRAS.530.1581K",
    "Kumar_2025": "https://ui.adsabs.harvard.edu/abs/2025ApJ...982..132K",
}


def get_atnf_references():
    """Wrapper for psrqpy.get_references() that ensures the cache is only Updated once."""
    ref_dict = psrqpy.get_references(version=ATNF_VER)
    if not isinstance(ref_dict, dict):
        # Reference error so update the cache
        ref_dict = psrqpy.get_references(version=ATNF_VER, updaterefcache=True)
    return ref_dict


def convert_atnf_ref(ref_code, ref_dict=None):
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
    # These one doesn't even have a title so returning maunally
    if ref_code == "san16":
        return "Sanpa-arsa_2016"
    elif ref_code == "gg74":
        return "Gomez-Gonzalez_1974"

    if ref_dict is None:
        ref_dict = get_atnf_references()

    try:
        ref_string = ref_dict[ref_code]
    except KeyError:
        return None

    # Find the parts we need
    if ref_string.startswith("eds "):
        # Remove the eds part which I think is a typo
        ref_string = ref_string[4:]
    author = ref_string.split(",")[0].replace(" ", "")

    # Get only author year part of the string, example string:
    # Anderson, S. B., Wolszczan, A., Kulkarni, S. R. & Prince, T. A., 1997. Observations of two millisecond pulsars in the globular cluster NGC 5904. ApJ, 482, 870-873.
    if "ArXiv" in ref_string:
        author_year_title = ref_string.split(". ArXiv")[0]
    elif "arXiv" in ref_string:
        author_year_title = ref_string.split(". arXiv")[0]
    elif "ApJ" in ref_string:
        author_year_title = ref_string.split(". ApJ")[0]
    elif "-" not in ref_string:
        # Has no refence code so skip the removal
        author_year_title = ref_string
    else:
        author_year_title = ref_string[: ref_string[:-1].rfind(".")]

    if "New York" in author_year_title:
        # Different format for American Institute of Physics, New York references
        author_year = author_year_title
    elif "IAU Circ. No" in author_year_title:
        # Different format for IAU Circular references
        author_year = author_year_title.split("IAU Circ. No")[0].replace("M.", "").replace("M5.", "")
    else:
        removal_patterns = [
            ". Phys. Rev",  # This journal isn't removed in previous logic so remove it here
            ". ATel",  # This journal isn't removed in previous logic so remove it here
            "(",  # Remove the brackets
            ":",  # Remove the colins
            "1E",  # Remove weird name convertion
            "NGC",  # NGC often in titles that ruin formatting
            "PSR",  # Parts of pulsar names are mistaken for years
            "Sgr",  # Parts of soft gamma ray repeaters are mistaken for years
        ]
        for pattern in removal_patterns:
            author_year_title = author_year_title.split(pattern)[0]
        author_year = author_year_title[: author_year_title.rfind(".")]

    # Loop through what is left to find the year
    for ref_part in author_year.split():
        if ref_part.endswith("."):
            # Remove trailing full stop
            ref_part = ref_part[:-1]
        if len(ref_part) == 4 and ref_part.isnumeric():
            year = ref_part
        elif len(ref_part) == 5 and ref_part[:-1].isnumeric():
            year = ref_part

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
        ref_dict = get_atnf_references()
    query_id = list(query["PSRJ"]).index(pulsar)

    # Find all flux queries from keys
    flux_queries = []
    for table_param in query.keys():
        if re.match(r"S\d*\d$", table_param) or re.match(r"S\d*G$", table_param):
            flux_queries.append(table_param)

    freq_all = []
    band_all = []
    flux_all = []
    flux_err_all = []
    references = []
    # Get all available data from dataframe and check for missing values
    for flux_query in flux_queries:
        flux = query[flux_query][query_id]

        # Check for flux
        if not np.isnan(flux):
            flux_all.append(flux)  # in mJy

            # Check for flux error. Sometimes error values don't exist, causing a key error in pandas
            flux_error_found = True
            try:
                flux_err = query[flux_query + "_ERR"][query_id]
                if np.isnan(flux_err) or flux_err == 0.0:
                    flux_error_found = False
            except KeyError:
                flux_error_found = False

            if not flux_error_found:
                logger.debug(
                    "{0} flux error for query: {1}, is zero. Assuming {2:.1f}% uncertainty".format(
                        pulsar, flux_query, assumed_error * 100
                    )
                )
                flux_err = flux * assumed_error
            flux_err_all.append(flux_err)  # in mJy

            # Converts key to frequency in MHz
            if flux_query.endswith("G"):
                # In GHz to convert to MHz
                freq = int(flux_query[1:-1]) * 1e3
            else:
                freq = int(flux_query[1:])
            freq_all.append(freq)
            band_all.append(None)

            # Grab reference code and convert to "Author Year" format
            # If reference is not found, fallback to ref_code
            ref_code = query[flux_query + "_REF"][query_id]
            ref = convert_atnf_ref(ref_code, ref_dict=ref_dict)
            if ref is None:
                logger.warning(f"no name found for reference {ref_code}")
                ref = ref_code
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
    ref_dict = get_atnf_references()
    jnames = list(query["PSRJ"])
    jname_cat = {}
    for jname in jnames:
        jname_cat[jname] = {}
        freq_all, band_all, flux_all, flux_err_all, references = flux_from_atnf(jname, query=query, ref_dict=ref_dict)
        for freq, band, flux, flux_err, ref in zip(freq_all, band_all, flux_all, flux_err_all, references):
            if ref not in jname_cat[jname].keys():
                jname_cat[jname][ref] = {
                    "Frequency MHz": [],
                    "Bandwidth MHz": [],
                    "Flux Density mJy": [],
                    "Flux Density error mJy": [],
                }
            jname_cat[jname][ref]["Frequency MHz"] += [freq]
            # Add Nones so the software can easily tell there are missing bandwidths
            jname_cat[jname][ref]["Bandwidth MHz"] += [band]
            jname_cat[jname][ref]["Flux Density mJy"] += [flux]
            jname_cat[jname][ref]["Flux Density error mJy"] += [flux_err]
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
    jnames = list(query["PSRJ"])
    jname_cat_dict = {}
    jname_cat_list = {}
    for jname in jnames:
        jname_cat_dict[jname] = {}
        # freq, flux, flux_err, references
        jname_cat_list[jname] = [[], [], [], [], []]

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
                jname_cat_list[jname][0] += cat_dict[jname]["Frequency MHz"]
                jname_cat_list[jname][1] += cat_dict[jname]["Bandwidth MHz"]
                jname_cat_list[jname][2] += cat_dict[jname]["Flux Density mJy"]
                jname_cat_list[jname][3] += cat_dict[jname]["Flux Density error mJy"]
                jname_cat_list[jname][4] += [cat_label] * len(cat_dict[jname]["Frequency MHz"])

    if not use_atnf:
        # return before including atnf
        return jname_cat_list

    # Add the atnf to the cataogues
    atnf_dict = all_flux_from_atnf(query=query)
    # refs that have errors that we plan to inform ATNF about
    atnf_incorrect_refs = [
        "Zhao_2019",
        "Mignani_2017",
        "Bell_2016",
        "Robinson_1995",
        "Johnston_1994",
        "Manchester_1996",
        "Xie_2019",
        "Han_2016",
        "Kramer_1999",
        "Kondratiev_2015",
        "Crawford_2001",
        "Michilli_2020",
        "Manchester_2013",
        "Brinkman_2018",
        "Fruchter_1990",
    ]
    # refs that are correct but where scaled to by their spectral index for the ATNF frequencies
    atnf_adjusted_refs = [
        "Lorimer_1995b",
        "Stovall_2015",
        "Sanidas_2019",
        "Wolszczan_1992",
        "Dembska_2014",
        "Kaur_2019",
        "Alam_2021",
        "Foster_1991",
    ]
    # refs that were rounded to different decimal places than the publications
    atnf_rounded_refs = [
        "Johnston_2018",
        "Dai_2015",
        "McEwen_2020",
        "McConnell_1991",
        "Bondonneau_2020",
        "Johnston_2021",
        "Bates_2011",
        "Han_2021",
        "Sayer_1997",
        "Lynch_2012",
        "Stovall_2014",
        "Crowter_2020",
        "Bilous_2016",
        "Frail_2016",
        "Gitika_2023",
        "Dembska_2015",
        "Wang_2024",
        "Keith_2024",
    ]
    # refs that have different uncertainties than published
    atnf_uncert_refs = [
        "Stairs_1999",
        "Kuzmin_2001",
        "Jankowski_2019",
        "Jankowski_2018",
        "Kramer_2003a",
        "Manchester_2001",
        "Morris_2002",
        "Zhang_2019",
    ]
    atnf_other_refs = [
        "Taylor_1993",  # excluding due to duplication of other references
        "Ahmad_2024",  # need to add this to the pulsar_spectra catalogue properly
    ]

    for jname in jnames:
        for ref in atnf_dict[jname].keys():
            # Remove "_atnf" from the end of  the reference
            raw_ref = ref[:-5]
            # Check if only_use or exclude allow this ref
            if only_use is not None:
                if raw_ref not in only_use:
                    # Not in only_use so skip
                    continue
            if exclude is None:
                exclude = []
            if (
                raw_ref
                in exclude
                + atnf_incorrect_refs
                + atnf_adjusted_refs
                + atnf_rounded_refs
                + atnf_uncert_refs
                + atnf_other_refs
            ):
                # exclude by skipping
                continue

            if raw_ref in jname_cat_dict[jname].keys():
                # Check for redundant data
                for freq, band, flux, flux_err in zip(
                    atnf_dict[jname][ref]["Frequency MHz"],
                    atnf_dict[jname][ref]["Bandwidth MHz"],
                    atnf_dict[jname][ref]["Flux Density mJy"],
                    atnf_dict[jname][ref]["Flux Density error mJy"],
                ):
                    if (
                        flux in jname_cat_dict[jname][raw_ref]["Flux Density mJy"]
                        and flux_err in jname_cat_dict[jname][raw_ref]["Flux Density error mJy"]
                    ):
                        logger.debug(
                            f"Redundant data  pulsar:{jname}  ref:{raw_ref}  freq:{freq}  flux:{flux}  flux_err:{flux_err}"
                        )
                    else:
                        # Update list
                        jname_cat_list[jname][0] += [freq]
                        jname_cat_list[jname][1] += [band]
                        jname_cat_list[jname][2] += [flux]
                        jname_cat_list[jname][3] += [flux_err]
                        jname_cat_list[jname][4] += [ref]
            else:
                # Update list
                for freq, band, flux, flux_err in zip(
                    atnf_dict[jname][ref]["Frequency MHz"],
                    atnf_dict[jname][ref]["Bandwidth MHz"],
                    atnf_dict[jname][ref]["Flux Density mJy"],
                    atnf_dict[jname][ref]["Flux Density error mJy"],
                ):
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
                jname_cat_dict[jname][ref]["Frequency MHz"] += [freq]
                jname_cat_dict[jname][ref]["Bandwidth MHz"] += [band]
                jname_cat_dict[jname][ref]["Flux Density mJy"] += [flux]
                jname_cat_dict[jname][ref]["Flux Density error mJy"] += [flux_err]
            else:
                # Make new
                jname_cat_dict[jname][ref] = {}
                jname_cat_dict[jname][ref]["Frequency MHz"] = [freq]
                jname_cat_dict[jname][ref]["Bandwidth MHz"] = [band]
                jname_cat_dict[jname][ref]["Flux Density mJy"] = [flux]
                jname_cat_dict[jname][ref]["Flux Density error mJy"] = [flux_err]
    return jname_cat_dict
