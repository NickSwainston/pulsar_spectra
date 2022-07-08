from pulsar_spectra.spectral_fit import find_best_spectral_fit
from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.models import calc_high_frequency_cutoff_emission_height

cat_dict = collect_catalogue_fluxes()
pulsar = 'J0452-1759'
freqs, fluxs, flux_errs, refs = cat_dict[pulsar]
model_name, m, _, _, _ = find_best_spectral_fit(pulsar, freqs, fluxs, flux_errs, refs)
if model_name == "high_frequency_cut_off_power_law":
    B_pc, u_B_pc, B_surf, B_lc, r_lc, z_e, u_z_e, z_percent, u_z_percent = calc_high_frequency_cutoff_emission_height(
        pulsar, 
        m.values[0],
        m.errors[0],
    )
    print(f"B_pc:    ({B_pc/1e11:.2f} +/- {u_B_pc/1e11:.2f})x10^11 G")
    print(f"B_surf:  {B_surf/1e12:.2f}x10^12 G")
    print(f"B_LC:    {B_lc:.2f} G")
    print(f"R_LC:    {r_lc:.0f} km")
    print(f"z_e:     {z_e:.1f} +/- {u_z_e:.1f} km")
    print(f"z/R_LC:  {z_percent:.2f} +/- {u_z_percent:.2f} %")
else:
    print("Not a power-law with high-frequency cut-off fit")
