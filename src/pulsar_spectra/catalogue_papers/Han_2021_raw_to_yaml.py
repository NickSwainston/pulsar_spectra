import yaml
import csv

with open("Han_2021_raw.tsv", "r") as raw_file:
    tsv_file = csv.reader(raw_file, delimiter="\t")
    lines = []
    for line in tsv_file:
        lines.append(line)

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]
    if len(row) == 0:
        continue
    if row[0].startswith("#") or row[0].startswith("PSR") or row[0] == '' or row[0].startswith('-'):
        continue

    pulsar = row[0].strip().replace("–", "-")
    # Discoveries which have since been well localised
    if pulsar == "J1837+0033g":
        pulsar = "J1837+0033"
    if pulsar == "J1844+0028g":
        pulsar = "J1844+0028"
    if pulsar == "J1848+0150g":
        pulsar = "J1848+0150"
    if pulsar == "J1849+0001g":
        pulsar = "J1849+0001"
    if pulsar == "J1849+0009g":
        pulsar = "J1849+0009"
    if pulsar == "J1849-0014g":
        pulsar = "J1849-0014"
    if pulsar == "J1850-0002g":
        pulsar = "J1850-0002"
    if pulsar == "J1850-0020g":
        pulsar = "J1850-0020"
    if pulsar == "J1852+0018g":
        pulsar = "J1852+0018"
    if pulsar == "J1852-0024g":
        pulsar = "J1852-0024"
    if pulsar == "J1852-0033g":
        pulsar = "J1852-0033"
    if pulsar == "J1852-0039g":
        pulsar = "J1852-0039"
    if pulsar == "J1853+0013g":
        pulsar = "J1853+0013"
    if pulsar == "J1853+0023g":
        pulsar = "J1853+0023"
    if pulsar == "J1855+0235g":
        pulsar = "J1855+0235"
    if pulsar == "J1856+0211g":
        pulsar = "J1856+0211"
    if pulsar == "J1857+0214g":
        pulsar = "J1857+0214"
    if pulsar == "J1857+0224g":
        pulsar = "J1857+0224"
    if pulsar == "J1859+0430g":
        pulsar = "J1859+0430"
    if pulsar == "J1901+0659g":
        pulsar = "J1901+0658"
    if pulsar == "J1903+0845g":
        pulsar = "J1903+0845"
    if pulsar == "J1903+0851g":
        pulsar = "J1903+0851"
    if pulsar == "J1904+0852g":
        pulsar = "J1904+0852"
    if pulsar == "J1905+0656g":
        pulsar = "J1905+0656"
    if pulsar == "J1905+0758g":
        pulsar = "J1905+0758"
    if pulsar == "J1905+0936g":
        pulsar = "J1905+0936"
    if pulsar == "J1906+0757g":
        pulsar = "J1906+0757"
    if pulsar == "J1914+0805g":
        pulsar = "J1914+0805"
    if pulsar == "J1916+0748g":
        pulsar = "J1916+07481"
    if pulsar == "J1916+1030Bg":
        pulsar = "J1916+10305"
    if pulsar == "J1917+0743g":
        pulsar = "J1917+0743"
    if pulsar == "J1926+1631g":
        pulsar = "J1926+1631"
    if pulsar == "J1928+1852g":
        pulsar = "J1928+1852"
    if pulsar == "J1930+1357g":
        pulsar = "J1930+1357"
    if pulsar == "J1953+1844g":
        pulsar = "J1953+1844"
    if pulsar == "J2017+2819g":
        pulsar = "J2017+2819"

    # Provisional pulsar names
    if pulsar.endswith("g"):
        pulsar = f"{pulsar.split('g')[0]}_P"

    flux = round(float(row[1]) / 1e3, 3)
    flux_err = round(float(row[1]) / 1e3* 0.5, 3)
    pulsar_dict[pulsar] = {
        "Frequency MHz":[1250.],
        "Bandwidth MHz":[450.],
        "Flux Density mJy":[flux],
        "Flux Density error mJy":[flux_err]
    }

with open("Han_2021.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)