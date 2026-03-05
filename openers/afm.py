try:
    import afmformats
    AFMFORMATS_AVAILABLE = True
except ImportError:
    AFMFORMATS_AVAILABLE = False

import openers._skeleton as skeleton
import numpy as np

NAME = 'AFM formats'
EXT = '*'

class opener(skeleton.prepare_opener):

    def open(self):
        if not AFMFORMATS_AVAILABLE:
            raise ImportError('afmformats is not installed. Install it with: pip install afmformats')
        dslist = afmformats.load_data(self.filename)
        self.curve.channels = dslist[0].columns
        print(dslist[0]["force"])
        self.curve.parameters['x']=float(dslist[0].metadata['position x'])
        self.curve.parameters['y']=float(dslist[0].metadata['position y'])
        self.curve.parameters['k']=float(dslist[0].metadata['spring constant'])
        for i in range(len(self.curve.channels)):
            if self.curve.channels[i].startswith('time'):
                self.curve.idTime = i
            elif self.curve.channels[i].startswith('force'):
                self.curve.idForce = i
            elif self.curve.channels[i].startswith('height (piezo)'):
                self.curve.idZ = i
        #
        #dslist[0]["force"]
        #Out[5]: 
        #array([-6.56678981e-10, -6.64172230e-10, -6.79510911e-10, ...,
        #    -7.61449435e-10, -7.68909858e-10, -7.58163174e-10])
        
        return self.curve