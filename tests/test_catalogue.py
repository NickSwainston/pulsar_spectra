#! /usr/bin/env python

import os
import yaml
import psrqpy

from pulsar_spectra.catalogue import collect_catalogue_fluxes, CAT_YAMLS, ADS_REF, ATNF_VER

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# formatter = logging.Formatter('%(asctime)s  %(name)s  %(lineno)-4d  %(levelname)-9s :: %(message)s')
# ch = logging.StreamHandler()
# ch.setFormatter(formatter)
# # Set up local logger
# logger.setLevel(logging.DEBUG)
# logger.addHandler(ch)
# logger.propagate = False
# # Loop over imported vcstools modules and set up their loggers
# for imported_module in sys.modules.keys():
#     if imported_module.startswith('pulsar_spectra'):
#         logging.getLogger(imported_module).setLevel(logging.DEBUG)
#         logging.getLogger(imported_module).addHandler(ch)
#         logging.getLogger(imported_module).propagate = False


def test_ref_duplicates_removed():
    """Tests if all of the ATNF references have been removed for our pulsar_spectra refs.
    """
    cat_dict = collect_catalogue_fluxes()
    for pulsar in cat_dict.keys():
        print(pulsar)
        ref_ps = []
        ref_atnf = []
        for ref in cat_dict[pulsar][4]:
            if 'ATNF' in ref:
                ref_atnf.append(ref[:-5])
            else:
                ref_ps.append(ref)
        for ref in ref_atnf:
            assert ref not in tuple(ref_ps)


def test_missing_ads_refs():
    """Check there are ADS references for all included publications.
    """
    for cat_file in CAT_YAMLS:
        cat_ref = os.path.basename(cat_file).split(".")[0]
        print(cat_ref)
        assert cat_ref in ADS_REF


def test_catalogue_format():
    """Check the pulsar names are correct and that all the keys are correct.
    """
    query = psrqpy.QueryATNF(version=ATNF_VER).pandas
    jnames = list(query['PSRJ'])
    for cat_file in CAT_YAMLS:
        print(cat_file)
        with open(cat_file, "r") as stream:
            cat_dict = yaml.safe_load(stream)
        for pulsar in cat_dict.keys():
            print(pulsar)
            # Below is a typo in ATNF v1.68
            if pulsar not in ("J1643-10"):
                assert pulsar in jnames
            assert 'Frequency MHz' in cat_dict[pulsar].keys()
            assert 'Bandwidth MHz' in cat_dict[pulsar].keys()
            assert 'Flux Density mJy' in cat_dict[pulsar].keys()
            assert 'Flux Density error mJy' in cat_dict[pulsar].keys()
            assert len(cat_dict[pulsar]['Frequency MHz']) == len(cat_dict[pulsar]['Bandwidth MHz']) ==\
                   len(cat_dict[pulsar]['Flux Density mJy' ]) == len(cat_dict[pulsar]['Flux Density error mJy'])
            # Check no zeros in cat
            for freq, band, flux, flux_err in zip(cat_dict[pulsar]['Frequency MHz'],
                                                  cat_dict[pulsar]['Bandwidth MHz'],
                                                  cat_dict[pulsar]['Flux Density mJy'],
                                                  cat_dict[pulsar]['Flux Density error mJy']):
                assert freq != 0.
                assert band != 0.
                assert flux != 0.
                assert flux_err != 0.



# TODO finish below
def todo_test_for_duplicate_data():
    """Tests if there is any duplicate data, usualy due to including data that a publication was referenceing (not their data).
    """
    # List of data that has been checked and are true duplicates (individual detections of the same value)
    exceptions = {
        # "J0206-4028": 1,
        # "J0401-7608": 1,
        # "J0421-0345": 1,
        # "J0536-7543": 1,
        # "J0631+1036": 1,
        # "J0809-4753": 1,
        # "J0820-4114": 1,
        # "J0840-5332": 1,
        # "J0751+1807": 1,
        # "J0904-4246": 1,
        # "J0904-7459": 1,
        # "J0907-5157": 1,
        # "J0908-4913": 1,
        # "J0909-7212": 1,
        # "J1012+5307": 1,
        # "J1012+5307": 2,
        # "J1012-2337": 1,
        # "J1056-6258": 1,
        # "J1057-7914": 1,
        # "J1059-5742": 1,
        # "J1112-6613": 1,
        # "J1116-4122": 1,
        # "J1136-5525": 1,
        # "J1146-6030": 1,
        # "J1305-6455": 1,
        # "J1312-5516": 1,
        # "J1316-6232": 1,
        # "J1320-5359": 1,
        # "J1326-5859": 1,
        # "J1341-6220": 2,
        # "J1401-6357": 1,
        # "J1428-5530": 1,
        # "J1512-5759": 1,
    }
    cat_dict = collect_catalogue_fluxes()
    for pulsar in cat_dict.keys():
        if pulsar in exceptions.keys():
            nexceptions = exceptions[pulsar]
        else:
            nexceptions = 0
        # make tuples of each flux trio
        flux_trios = []
        freqs, fluxs, flux_errs, refs = cat_dict[pulsar]
        for freq, flux, flux_err in zip(freqs, fluxs, flux_errs):
            flux_trios.append((freq,flux,flux_err))
        # Check all values are unique
        duplicates = set([x for x in flux_trios if flux_trios.count(x) > 1])
        if len(duplicates) > nexceptions:
            print(pulsar)
            print(duplicates)
            #assert len(duplicates) == nexceptions

if __name__ == "__main__":
    """
    Tests the relevant functions in catalogue.py
    """
    # introspect and run all the functions starting with 'test'
    for f in dir():
        if f.startswith('test'):
            print(f)
            globals()[f]()
