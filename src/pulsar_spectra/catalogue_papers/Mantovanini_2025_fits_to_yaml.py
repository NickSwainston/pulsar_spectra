# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "astropy",
# ]
# ///

import yaml
from astropy.table import Table


def main() -> None:
    t = Table.read("Mantovanini_2025_matched_pulsars.fits")

    freqs = []
    for colname in t.colnames:
        if colname.startswith("peak_flux_"):
            freqs.append(int(colname.split("_")[2].split("MHz")[0]))

    pulsar_dict = {}
    for row in range(len(t)):
        psrj = str(t[row]["PSRJ"])

        if psrj == "J0737-3039B":
            # The flux at this position originates from the A pulsar, so they have been falsely
            # attributed to the B pulsar here, hence we exclude them.
             continue
        elif psrj in ["J1534-46", "J1708-52"]:
            # There are multiple GLEAM-X sources associated with these pulsars as they lie on the
            # Galactic plane, and there is not enough independent spectral data to disambiguate
            # which of these sources are the pulsar. Therefore, as a precaution (in case these
            # fluxes have been misassociated) we exclude them.
            # See Section 5.1 and Figure 6 of Mantovanini et al. (2025).
            continue
        elif psrj == "J1848+0150g":
            psrj = "J1848+0150"
        elif psrj == "J1902+0809g":
            psrj = "J1902+0809_P"

        psr_freqs = []
        psr_fluxes = []
        psr_flux_errs = []
        for freq in freqs:
            psr_flux = float(t[row][f"peak_flux_{freq:03d}MHz"])*1e3
            psr_flux_err = float(t[row][f"err_peak_flux_{freq:03d}MHz"])*1e3

            # Fluxes that are negative or have >100% error are due to low S/N and can be
            # considered non-detections or upper limits, so we exclude them
            # TODO: Include these as upper limits
            if psr_flux <= 0.0:
                print(f"FLUX<0: {psrj}: freq={freq}MHz flux={psr_flux}mJy err={psr_flux_err}mJy")
                continue
            if psr_flux_err/psr_flux >= 1.0:
                print(f"ERR>100%: {psrj}: freq={freq}MHz flux={psr_flux}mJy err={psr_flux_err}mJy")
                continue

            psr_freqs.append(float(freq))
            psr_fluxes.append(psr_flux)
            psr_flux_errs.append(psr_flux_err)

        pulsar_dict[psrj] = {
            "Frequency MHz": psr_freqs,
            "Bandwidth MHz": [7.68] * len(psr_freqs),
            "Flux Density mJy": psr_fluxes,
            "Flux Density error mJy": psr_flux_errs,
        }

    with open("Mantovanini_2025.yaml", "w") as cat_file:
        yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)


if __name__ == "__main__":
    main()
