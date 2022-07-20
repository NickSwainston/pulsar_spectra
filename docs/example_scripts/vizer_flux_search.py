import psrqpy
from astroquery.vizier import Vizier
import logging
import sys

file_path = 'pulsar_flux_vixier_tables.txt'

file_handler = logging.FileHandler(filename=file_path)
handlers = [file_handler]

logging.basicConfig(
    level=logging.DEBUG,
    handlers=handlers
)
logger = logging.getLogger('LOGGER_NAME')

jname = "J0030+0451"

vizier_class = Vizier
logger.info(vizier_class.ucd)
vizier_class.ucd = '(phot.flux*)'
logger.info(vizier_class.ucd)
#result = vizier_class.get_catalogs('J/A+A/626/A104/tablea1')

query = psrqpy.QueryATNF(params=['PSRJ', 'PSRB']).pandas
# pid = list(query['PSRJ']).index(jname)
# bname = query['PSRB'][pid]
# result = vizier_class.query_object([f"PSR {jname}", f"PSR {bname}"])
all_tables = []
already_checked = []
found_catalogues = {}
for psr in (list(query['PSRB']) + list(query['PSRJ'])):
    logger.info(psr)
    if type(psr) == float:
        # skip nans
        continue
    result = vizier_class.query_object(f"PSR {psr}")
    logger.info(len(result.keys()))
    all_tables += result.keys()

    # loop over tables and check if we care
    for tab_name in result.keys():
        if tab_name in already_checked:
            continue
        else:
            already_checked.append(tab_name)
        cat_name = "/".join(tab_name.split("/")[:-1])
        for col in result[tab_name].keys():
            if result[tab_name][col].unit is not None:
                #logger.info(str(result[tab_name][col].unit))
                if "Jy" in str(result[tab_name][col].unit):
                    if cat_name in found_catalogues.keys():
                        if tab_name in found_catalogues[cat_name].keys():
                            found_catalogues[cat_name][tab_name].append(col)
                        else:
                            found_catalogues[cat_name][tab_name] =[result[tab_name], col]
                    else:
                        found_catalogues[cat_name] = {}

logger.info("Query end")
distinct_tables = list(set(all_tables))
logger.info(len(all_tables))
logger.info(len(distinct_tables))
logger.info(distinct_tables)

for cat_name in found_catalogues.keys():
    logger.info("\n")
    logger.info(cat_name)
    logger.info(f"link:        https://vizier.cfa.harvard.edu/viz-bin/VizieR?-source={cat_name}")
    for tab_name in found_catalogues[cat_name].keys():
        result = found_catalogues[cat_name][tab_name][0]
        logger.info(f"\n  {tab_name}")
        logger.info(f"  description: {result.meta['description']}")
        logger.info(f"  possible flux columns: {found_catalogues[cat_name][tab_name][1:]}")
        logger.info(f"  Number of pulsars: {len(result)}")

