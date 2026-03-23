#!/usr/bin/env python
import numpy as np
import h5py

def find_dataset_by_name(segment, name):
    for dataset_key in segment:
        dataset = segment[dataset_key]
        if ('signal_name' in dataset.attrs) and (dataset.attrs['signal_name'] == name):
            return np.array(dataset), dataset.attrs
    return None, None

with h5py.File('testNHF/gut.nhf', 'r') as f:
    subgroup = f['/group_0000/subgroup_0000/']
    
    D, Dattr = find_dataset_by_name(subgroup, 'Deflection')
    Z, Zattr = find_dataset_by_name(subgroup, 'Position Z')
    
    general_fw = f['/group_0000/']
    gen_att = {key: general_fw.attrs[key] for key in general_fw.attrs}
    
    signal_minmax = Dattr['signal_minmax']
    invols = gen_att['spm_probe_calibration_deflection_sensitivity']
    k = gen_att['spm_probe_calibration_spring_constant']
    
    # Current implementation
    coeDV = (Dattr['signal_calibration_max'] - Dattr['signal_calibration_min']) / (signal_minmax[1] - signal_minmax[0])
    coeD = coeDV * invols
    
    print("="*70)
    print("CURRENT NHF OPENER - DEFLECTION CONVERSION")
    print("="*70)
    print(f"signal_minmax: {signal_minmax}")
    print(f"signal_calibration_min: {Dattr['signal_calibration_min']} V")
    print(f"signal_calibration_max: {Dattr['signal_calibration_max']} V")
    print(f"invols (deflection_sensitivity): {invols:.3e}")
    print(f"coeDV (int32 to V): {coeDV:.3e} V/count")
    print(f"coeD (int32 to m): {coeD:.3e} m/count")
    print()
    
    # Sample values
    max_int32 = signal_minmax[1]
    min_int32 = signal_minmax[0]
    
    print("Sample conversions:")
    print(f"  Max int32 ({max_int32:+.2e}) -> {max_int32*coeD:.3e} m = {max_int32*coeD*1e9:.1f} nm = {max_int32*coeD*1e6:.2f} µm")
    print(f"  Min int32 ({min_int32:+.2e}) -> {min_int32*coeD:.3e} m = {min_int32*coeD*1e9:.1f} nm = {min_int32*coeD*1e6:.2f} µm")
    
    # Actual data range
    D_min = np.nanmin(D)
    D_max = np.nanmax(D)
    print(f"\nActual data in file:")
    print(f"  Min value: {D_min:+.2e} -> {D_min*coeD:.3e} m = {D_min*coeD*1e9:.1f} nm")
    print(f"  Max value: {D_max:+.2e} -> {D_max*coeD:.3e} m = {D_max*coeD*1e9:.1f} nm")
    
    print("\n" + "="*70)
    print("HYPOTHESIS: invols might be INVERSE (1/sensitivity)")
    print("="*70)
    coeDV_alt = coeDV / invols  # if invols is actually V/m not m/V
    print(f"If invols is V/m instead of m/V:")
    print(f"  coeD (corrected) = coeDV / invols = {coeDV_alt:.3e} m/count")
    print(f"  Max deflection: {max_int32*coeDV_alt:.3e} m = {max_int32*coeDV_alt*1e9:.1f} nm = {max_int32*coeDV_alt*1e6:.2f} µm")
    print(f"  Actual max: {D_max*coeDV_alt:.3e} m = {D_max*coeDV_alt*1e9:.1f} nm = {D_max*coeDV_alt*1e6:.2f} µm")
    ratio = (max_int32*coeDV_alt) / (max_int32*coeD) if coeD != 0 else 0
    print(f"  Ratio (correction factor): {ratio:.0e}")
    
    print("\n" + "="*70)
    print("HYPOTHESIS: Missing 1e-3 or 1e3 factor")
    print("="*70)
    for factor_exp in [-3, 3]:
        factor = 10**factor_exp
        coeD_scaled = coeD * factor
        print(f"If coeD * 1e{factor_exp}:")
        print(f"  Max deflection: {max_int32*coeD_scaled*1e6:.2f} µm")
        print(f"  Actual max: {D_max*coeD_scaled*1e6:.2f} µm")
    
    print("\n" + "="*70)
    print("SPRING CONSTANT CHECK")
    print("="*70)
    print(f"Spring constant: {k:.3e} N/m")
    force_from_max_deflection_current = max_int32 * coeD * k
    print(f"Force from max deflection (current): {force_from_max_deflection_current:.3e} N = {force_from_max_deflection_current*1e9:.1f} nN")
    force_from_max_deflection_alt = max_int32 * coeDV_alt * k
    print(f"Force from max deflection (if invols inverted): {force_from_max_deflection_alt:.3e} N = {force_from_max_deflection_alt*1e9:.1f} nN")
