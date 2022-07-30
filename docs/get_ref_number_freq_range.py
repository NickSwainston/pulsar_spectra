import psrqpy
import yaml

from pulsar_spectra.catalogue import all_flux_from_atnf
from pulsar_spectra.catalogue import CAT_YAMLS

paper_format = False

# sort by year then name
name_year = []
for ref in CAT_YAMLS:
    name_year.append([ref.split("/")[-1].split(".")[0].split("_")[0], ref.split("/")[-1].split(".")[0].split("_")[-1], ref])
name_year.sort(key=lambda x: (x[1], x[0]))
print(name_year)
CAT_YAMLS = [ x[-1] for x in name_year ]
print(CAT_YAMLS)

# go through all the papers and count the pulsars and frequency range
query = psrqpy.QueryATNF().pandas
# Make a dictionary for each pulsar
jnames = list(query['PSRJ'])
jname_cat_dict = {}
jname_cat_list = {}
for jname in jnames:
    jname_cat_dict[jname] = {}
    # freq, flux, flux_err, references
    jname_cat_list[jname] = [[],[],[],[]]

# Add the antf to the cataogues
antf_dict = all_flux_from_atnf()
all_freq = []
pulsar_count = 0
pulsar_track = []
for jname in jnames:
    for ref in antf_dict[jname].keys():
        if len(antf_dict[jname][ref]['Frequency MHz']) > 0:
            all_freq += antf_dict[jname][ref]['Frequency MHz']
            if jname not in pulsar_track:
                pulsar_count += 1
                pulsar_track.append(jname)
if paper_format:
    print(f"ATNF pulsar catalogue & {pulsar_count} & {int(min(all_freq))}-{int(max(all_freq))} \\\\")
else:
    print(f'"ATNF pulsar catalogue","{pulsar_count}","{int(min(all_freq))}-{int(max(all_freq))}","`Catalogue website <https://www.atnf.csiro.au/research/pulsar/psrcat/>`_"')

# dictionary of ADS links
ads_dict = {
    "Sieber_1973": "https://ui.adsabs.harvard.edu/abs/1973A%26A....28..237S/abstract",
    "Bartel_1978": "https://ui.adsabs.harvard.edu/abs/1978A%26A....68..361B/abstract",
    "Izvekova_1981": "https://ui.adsabs.harvard.edu/abs/1981Ap%26SS..78...45I/abstract",
    "Lorimer_1995": "https://ui.adsabs.harvard.edu/abs/1995MNRAS.273..411L/abstract",
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
    "Kramer_2003": "https://ui.adsabs.harvard.edu/abs/2003MNRAS.342.1299K/abstract",
    "Han_2021" : "https://ui.adsabs.harvard.edu/abs/2021RAA....21..107H/abstract",
}
# Loop over catalogues and put them into a dictionary
for cat_file in CAT_YAMLS:
    cat_label = cat_file.split("/")[-1].split(".")[0]

    # Load in the dict
    with open(cat_file, "r") as stream:
        cat_dict = yaml.safe_load(stream)
    pulsar_count = len(cat_dict.keys())

    all_freq = []
    # Find which pulsars in the dictionary
    for jname in jnames:
        if jname in cat_dict.keys():
            # Update dict
            jname_cat_dict[jname][cat_label] = cat_dict[jname]
            # add freq
            all_freq += cat_dict[jname]['Frequency MHz']

    # output result
    if paper_format:
        cat_label = cat_label.replace("_", "")
        print(f"\cite{{{cat_label}}} & {pulsar_count} & {int(min(all_freq))}-{int(max(all_freq))} \\\\")
    else:
        ads_link = ads_dict[cat_label]
        if cat_label == "Sieber_1973":
            cat_label = "Sieber (1973)"
        else:
            author = " ".join(cat_label.split("_")[:-1])
            year = cat_label.split("_")[-1]
            cat_label = f"{author} et al. ({year})"
        print(f'"{cat_label}","{pulsar_count}","{int(min(all_freq))}-{int(max(all_freq))}","`ADS <{ads_link}>`_"')
    #print(all_freq)
