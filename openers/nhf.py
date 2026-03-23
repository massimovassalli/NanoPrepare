import openers._skeleton as skeleton
import numpy as np
import h5py

NAME = 'NHF Nanosurf basic opener'
EXT = '.nhf'

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

def read_curve_segment(subgroup, index):
    T, _ = find_dataset_by_name(subgroup, 'Time')
    D, Dattr = find_dataset_by_name(subgroup, 'Deflection')
    Z, Zattr = find_dataset_by_name(subgroup, 'Position Z')
    block_sizes = np.array(find_block_size_dataset(subgroup), dtype=int)

    istart = np.sum(block_sizes[:index])
    iend = istart + block_sizes[index]

    coeZ = -(Zattr['signal_calibration_max'] - Zattr['signal_calibration_min']) / (Zattr['signal_minmax'][1] - Zattr['signal_minmax'][0])
    coeDV = (Dattr['signal_calibration_max'] - Dattr['signal_calibration_min']) / (Dattr['signal_minmax'][1] - Dattr['signal_minmax'][0])
    invols = subgroup.parent.attrs['spm_probe_calibration_deflection_sensitivity']
    coeD = coeDV * invols

    return np.transpose(np.vstack([dset[istart:iend] for dset in [T, Z * coeZ, D * coeD]]))

class opener(skeleton.prepare_opener):
    def isMultiple(self):
        data=[]
        innerattr = []
        with h5py.File(self.filename, 'r') as f:
            subgroup = f['/group_0000/']
            attributes = {key: subgroup.attrs[key] for key in subgroup.attrs}
        x,y = attributes['rect_axis_size']
        self.number = x*y
        return True

    def open(self,number=False,limit=False):

        with h5py.File(self.filename, 'r') as f:
            general_fw = f['/group_0000/']
            gen_att = {key: general_fw.attrs[key] for key in general_fw.attrs}
            xdata = f['/group_0000/dataset_0000/'][:]
            ydata = f['/group_0000/dataset_0001/'][:]
            segment_groups = find_segment_groups(general_fw)
            
            if not number:
                number = 1
            index = number - 1
            
            k = gen_att['spm_probe_calibration_spring_constant']
            self.curve.parameters['k'] = k
            self.curve.parameters['x'] = xdata[index]
            self.curve.parameters['y'] = ydata[index]

            segments = [read_curve_segment(subgroup, index) for subgroup in segment_groups]

        self.curve.channels = ['Time','Z Position [m]','Deflection [m]']
        self.curve.idTime = 0
        self.curve.idForce = 2
        self.curve.idZ = 1
        self.curve.isDeflection = True
        self.curve.tip['value']=1e-5

        self.curve.data = np.vstack(segments)
        for data in segments:
            self.curve.attach(data)

        
        return self.curve