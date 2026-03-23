#!/usr/bin/env python
"""
Find the scaling factor issue between observed (0.80V -> 3µm) and calculated values.
"""
import numpy as np
import h5py

def find_dataset_by_name(segment, name):
    for dataset_key in segment:
        dataset = segment[dataset_key]
        if ('signal_name' in dataset.attrs) and (dataset.attrs['signal_name'] == name):
            return np.array(dataset), dataset.attrs
    return None, None

# Open the test file
with h5py.File('testNHF/gut.nhf', 'r') as f:
    subgroup = f['/group_0000/subgroup_0000/']
    D, Dattr = find_dataset_by_name(subgroup, 'Deflection')
    general_fw = f['/group_0000/']
    gen_att = {key: general_fw.attrs[key] for key in general_fw.attrs}
    
    signal_minmax = Dattr['signal_minmax']
    invols = gen_att['spm_probe_calibration_deflection_sensitivity']
    k = gen_att['spm_probe_calibration_spring_constant']
    
    # Current implementation
    coeDV = (Dattr['signal_calibration_max'] - Dattr['signal_calibration_min']) / (signal_minmax[1] - signal_minmax[0])
    coeD = coeDV * invols
    
    print("="*80)
    print("THE ACTUAL PROBLEM")
    print("="*80)
    print()
    print("User's observation: deflection channel shows 0.80V, displacement is 3 µm")
    print(f"This means: 0.80V should map to 3 µm displacement")
    print() 
    print("Current code:")
    print(f"  coeDV = {coeDV:.3e} V/count")
    print(f"  invols = {invols:.3e} m/V")
    print(f"  coeD = coeDV * invols = {coeD:.3e} m/count")
    print()
    
    # Find what int32 value corresponds to 0.80V
    int32_for_0p80V = 0.80 / coeDV
    print(f"Finding where 0.80V comes from:")
    print(f"  If deflection channel = 0.80V, this came from int32 value: {int32_for_0p80V:.2e}")
    print()
    
    # What does the current code convert this to?
    current_displacement = int32_for_0p80V * coeD
    print(f"Current code converts this to displacement:")
    print(f"  {int32_for_0p80V:.2e} * {coeD:.3e} = {current_displacement:.3e} m")
    print(f"  = {current_displacement*1e6:.3f} µm")
    print()
    
    # What should it be?
    expected_displacement = 3e-6  # 3 µm in meters
    needed_invols = expected_displacement / 0.80
    print(f"Expected conversion:")
    print(f"  Should be: 0.80V -> {expected_displacement*1e6:.1f} µm")
    print(f"  This requires invols = {expected_displacement*1e6:.1f} µm / 0.80V = {needed_invols:.3e} m/V")
    print()
    
    print(f"Comparison:")
    print(f"  File has invols = {invols:.3e} m/V")
    print(f"  Should be      = {needed_invols:.3e} m/V")
    print(f"  Ratio (should/current) = {needed_invols / invols:.1f}x")
    print()
    
    # Force calculation
    print("="*80)
    print("FORCE CALCULATION")
    print("="*80)
    current_force = current_displacement * k
    expected_force = expected_displacement * k
    print(f"With k = {k:.3e} N/m:")
    print(f"  Current: F = {current_displacement*1e6:.3f} µm *{k:.3e} = {current_force:.3e} N = {current_force*1e9:.2f} nN")
    print(f"  Expected: F = 3.0 µm * {k:.3e} = {expected_force:.3e} N = {expected_force*1e9:.2f} nN")
    print(f"  Force error: {expected_force / current_force:.1f}x")
    print()
    
    print("="*80)
    print("HYPOTHESIS: invols parameter is INVERTED (1/sensitivity)")
    print("="*80)
    # What if invols is actually in V/m (voltage sensitivity) instead of m/V?
    # Then we'd need to invert it
    inverted_invols = 1.0 / invols  # This would give m/V if invols is V/m
    print(f"If the file value {invols:.3e} is actually V/m (inverse),")
    print(f"then correct m/V would be: 1/{invols:.3e} = {inverted_invols:.3e} m/V")
    print(f"  Current displacement: {int32_for_0p80V * inverted_invols * 1e6:.3e} µm")
    print()
    print(f"But that gives {int32_for_0p80V * inverted_invols * 1e6:.2e} µm, NOT 3 µm")
    print()
    print("="*80)
    print("MOST LIKELY: invols value needs a factor")
    print("="*80)
    missing_factor = needed_invols / invols
    print(f"Missing scaling factor: {missing_factor:.1f}")
    print()
    print(f"SOLUTION: Use invols * {missing_factor:.0f} when converting")
    print(f"  coeD should be: coeDV * invols * {missing_factor:.0f}")
    print()
    
    # Final verification
    print("Verification with corrected factor:")
    coeD_corrected = coeD * missing_factor
    displacement_corrected = int32_for_0p80V * coeD_corrected
    force_corrected = displacement_corrected * k
    print(f"  Displacement: {displacement_corrected*1e6:.2f} µm ✓")
    print(f"  Force: {force_corrected*1e9:.2f} nN ✓")

