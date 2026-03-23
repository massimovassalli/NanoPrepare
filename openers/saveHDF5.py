
import h5py

class saveHDF5(object):
    def __init__(self,fname) -> None:
        self.filename = fname
        self.selectedsegment = 0
        self.curves=[]
        
    def addCurve(self, curve):
        self.curves.append(curve)
    
    def setSegment(self, number):
        self.selectedsegment = number
        
    def save(self):
        hd = h5py.File(self.filename,'w')
        hd.attrs['selectedSegment']=self.selectedsegment
        hd.attrs['curves']=len(self.curves)
        i=0
        for curve in self.curves:
            name = 'curve'+str(i)
            i+=1
            cv = hd.create_group(name)
            cv.attrs['filename']=str(curve.filename)
            cv.attrs['spring_constant']=curve.parameters['k']
            cv.attrs['x-position']=curve.parameters['x']
            cv.attrs['y-position']=curve.parameters['y']
            cv.attrs['segments']=len(curve.segments)
            cv.attrs['selectedSegment']=self.selectedsegment
            tip = cv.create_group('tip')
            for key in curve.tip:
                tip.attrs[key]=curve.tip[key]
            k=0            
            for segment in curve.segments:
                dataseg = cv.create_group(f'segment{k}')
                k+=1
                dataseg.attrs['mode']=''
                named = [curve.idTime,curve.idZ,curve.idForce]
                names = ['Time','Z','Force']
                for idname,name in zip(named,names):
                    dt = segment.data[:,idname]
                    if idname == curve.idForce and curve.isDeflection is True:
                        dt = dt * curve.parameters['k']
                    dataseg.create_dataset(name,data=dt)                
                for j in range(len(curve.channels)):
                    if j not in named:
                        dataseg.create_dataset(curve.channels[j],data=segment.data[:,j])                                        
        hd.close()