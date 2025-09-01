import psrqpy
import yaml
from pulsar_spectra.catalogue import ADS_REF, ATNF_VER, CAT_YAMLS, all_flux_from_atnf

paper_format = False

# sort by year then name
name_year = []
for ref in CAT_YAMLS:
    name_year.append(
        [ref.split("/")[-1].split(".")[0].split("_")[0], ref.split("/")[-1].split(".")[0].split("_")[-1], ref]
    )
name_year.sort(key=lambda x: (x[1], x[0]))
print(name_year)
CAT_YAMLS = [x[-1] for x in name_year]
print(CAT_YAMLS)

# go through all the papers and count the pulsars and frequency range
query = psrqpy.QueryATNF(version=ATNF_VER).pandas
# Make a dictionary for each pulsar
jnames = list(query["PSRJ"])
jname_cat_dict = {}
jname_cat_list = {}
for jname in jnames:
    jname_cat_dict[jname] = {}
    # freq, flux, flux_err, references
    jname_cat_list[jname] = [[], [], [], []]

# Add the atnf to the cataogues
atnf_dict = all_flux_from_atnf()
all_freq = []
pulsar_count = 0
pulsar_track = []
for jname in jnames:
    for ref in atnf_dict[jname].keys():
        if len(atnf_dict[jname][ref]["Frequency MHz"]) > 0:
            all_freq += atnf_dict[jname][ref]["Frequency MHz"]
            if jname not in pulsar_track:
                pulsar_count += 1
                pulsar_track.append(jname)


with open("papers_in_catalogue.csv", "w") as output:
    if paper_format:
        output.write(f"ATNF pulsar catalogue & {pulsar_count} & {int(min(all_freq))}-{int(max(all_freq))} \\\\\n")
    else:
        output.write(
            f'"ATNF pulsar catalogue","{pulsar_count}","{int(min(all_freq))}-{int(max(all_freq))}","`Catalogue website <https://www.atnf.csiro.au/research/pulsar/psrcat/>`_"\n'
        )

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
                all_freq += cat_dict[jname]["Frequency MHz"]

        # output result
        if paper_format:
            cat_label = cat_label.replace("_", "")
            output.write(f"\cite{{{cat_label}}} & {pulsar_count} & {int(min(all_freq))}-{int(max(all_freq))} \\\\\n")
        else:
            ads_link = ADS_REF[cat_label]
            if cat_label == "Sieber_1973":
                cat_label = "Sieber (1973)"
            else:
                author = " ".join(cat_label.split("_")[:-1])
                year = cat_label.split("_")[-1]
                cat_label = f"{author} et al. ({year})"
            output.write(
                f'"{cat_label}","{pulsar_count}","{int(min(all_freq))}-{int(max(all_freq))}","`ADS <{ads_link}>`__"\n'
            )
        # print(all_freq)
