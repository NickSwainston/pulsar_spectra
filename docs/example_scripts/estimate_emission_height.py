from pulsar_spectra.models import calc_high_frequency_cutoff_emission_height

B_pc, u_B_pc, z_e, u_z_e, r_LC, u_r_LC, z_percent, u_z_percent = calc_high_frequency_cutoff_emission_height("J0452-1759", 1.5e9, 25e6)

print(f"B_pc:   ({B_pc/1e11:.2f} +/- {u_B_pc/1e11:.2f})x10^11 G")
print(f"z_e:    {z_e:.1f} +/- {u_z_e:.1f} km")
print(f"R_LC:   {r_LC:.7f} +/- {u_r_LC:.7f} km")
print(f"z/R_LC: {z_percent:.3f} +/- {u_z_percent:.3f} %")
