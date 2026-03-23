import numpy as np
from PySide6.QtWidgets import QApplication, QProgressDialog
from PySide6.QtCore import Qt
import h5py

def find_dataset_by_name(segment, name):
    for dataset_key in segment:
        dataset = segment[dataset_key]
        if ('signal_name' in dataset.attrs) and (dataset.attrs['signal_name'] == name):
            return np.array(dataset),dataset.attrs
      
def find_block_size_dataset(segment):
    for dataset_key in segment:
        dataset = segment[dataset_key]
        if 'dataset_block_size_id' in dataset.attrs:
            return dataset

def find_segment_groups(group):
    segments = []
    for key in group:
        item = group[key]
        if isinstance(item, h5py.Group) and 'segment_index' in item.attrs:
            segments.append(item)
    segments.sort(key=lambda item: item.attrs['segment_index'])
    return segments

def read_curve_segment(subgroup, index, invols):
    T, _ = find_dataset_by_name(subgroup, 'Time')
    D, Dattr = find_dataset_by_name(subgroup, 'Deflection')
    Z, Zattr = find_dataset_by_name(subgroup, 'Position Z')
    block_sizes = np.array(find_block_size_dataset(subgroup), dtype=int)

    istart = np.sum(block_sizes[:index])
    iend = istart + block_sizes[index]

    coeZ = -(Zattr['signal_calibration_max'] - Zattr['signal_calibration_min']) / (Zattr['signal_minmax'][1] - Zattr['signal_minmax'][0])
    coeDV = (Dattr['signal_calibration_max'] - Dattr['signal_calibration_min']) / (Dattr['signal_minmax'][1] - Dattr['signal_minmax'][0])
    coeD = coeDV * invols

    return np.transpose(np.vstack([dset[istart:iend] for dset in [T, Z * coeZ, D * coeD]]))

def open(filename,limit = False):
    data=[]
    innerattr = []
    with h5py.File(filename, 'r') as f:
        subgroup = f['/group_0000/']
        attributes = {key: subgroup.attrs[key] for key in subgroup.attrs}
        x,y = attributes['rect_axis_size']
        ncurves = x*y
        if limit is not False:
            ncurves = limit        
        general_fw = f['/group_0000/']
        gen_att = {key: general_fw.attrs[key] for key in general_fw.attrs}
        xdata = f['/group_0000/dataset_0000/'][:]
        ydata = f['/group_0000/dataset_0001/'][:]
        segment_groups = find_segment_groups(general_fw)
        
        k = gen_att['spm_probe_calibration_spring_constant']
        invols = gen_att['spm_probe_calibration_deflection_sensitivity']
        channels = ['Time','Z Position [m]','Deflection [m]']
        curves = []
        coordinates = []
        
        # Create a progress dialog
        progress_dialog = QProgressDialog(f"Opening {ncurves} curves...", "Cancel", 0, ncurves)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)

        for number in range(ncurves):
            if progress_dialog.wasCanceled():
                break
            coordinates.append((xdata[number],ydata[number]))
            segment_data = [read_curve_segment(subgroup, number, invols) for subgroup in segment_groups]
            datai = np.vstack(segment_data)
            curves.append(datai)
            # Update the progress dialog
            progress_dialog.setValue(number + 1)
        progress_dialog.setValue(ncurves)
        
    return curves,coordinates,k

def save(filename,curves,coordinates,k,radius,limit=False):
    hd = h5py.File(filename,'w')
    hd.attrs['selectedSegment']=0
    hd.attrs['curves']=len(curves)
    i=0
    ncurves = len(curves)
    if limit is not False:
        ncurves = limit
    # Create a progress dialog
    progress_dialog = QProgressDialog(f"Saving {ncurves} curves...", "Cancel", 0, ncurves)
    progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
    progress_dialog.setMinimumDuration(0)
    for i in range(ncurves):
        curve = curves[i]
        name = 'curve'+str(i)        
        cv = hd.create_group(name)
        cv.attrs['filename']=str(filename)
        cv.attrs['spring_constant']=k
        cv.attrs['x-position']=coordinates[i][0]
        cv.attrs['y-position']=coordinates[i][1]
        cv.attrs['segments']=1
        cv.attrs['selectedSegment']=0
        tip = cv.create_group('tip')
        tip.attrs['geometry']='sphere'
        tip.attrs['parameter']='Radius'
        tip.attrs['unit']='m'
        tip.attrs['value']=radius*1e-6
        dataseg = cv.create_group(f'segment0')
        dataseg.attrs['mode']=''
        names = ['Time','Z','Force']
        for icv in range(3):
            name = names[icv]
            dt = curve[:,icv]
            if icv == 2:
                dt = dt * k
            dataseg.create_dataset(name,data=dt)         
        progress_dialog.setValue(i)
    progress_dialog.setValue(ncurves)       
    hd.close()