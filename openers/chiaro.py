
import openers._skeleton as skeleton
import numpy as np

NAME = 'Chiaro Optics11'
EXT = '.txt'
ENCODING = 'latin1'

def cross(x1, x2, th, dth):
    th1 = th+dth
    th2 = th-dth
    if np.sign(x1-th1) != np.sign(x2-th1):
        return True
    if np.sign(x1-th2) != np.sign(x2-th2):
        return True
    return False

def getNodes(curve,mode='safe',value=30*1e-9):
        if mode=='safe':
            nodi = [] 
            curtime = curve.parameters['SMDuration']
            #nodi.append(np.argmin((self.data['time']-curtime)**2))   
            nodi.append(0)        
            time = curve.data[:,curve.idTime]
            for seg in curve.protocols:
                curtime += seg[1]
                nodi.append( np.argmin((time-curtime)**2) )     
        elif mode=='euristic':
            sign = +1
            nodi = []
            nodi.append(0)
            wait = 0
            Z = curve.data[:,curve.idZ]
            T = curve.data[:,curve.idTime]
            actualPos = 2
            for nextThreshold, nextTime in curve.protocols:
                for j in range(actualPos, len(Z)):
                    if T[j] > wait + nextTime:
                        crossp = Z[j-1]>=nextThreshold*1e-9 and Z[j]<nextThreshold*1e-9
                        crossm = Z[j-1]<=nextThreshold*1e-9 and Z[j]>nextThreshold*1e-9
                        if crossp or crossm:
                            nodi.append(j)
                            actualPos = j
                            wait = T[j]
                            break
            nodi.append(len(Z)-1)   
        elif mode=='poking':
            nodi = [0]
            F = curve.data[:,curve.idForce]
            nodi.append(np.argmin( (F-curve.parameters['max_load'])**2 ))
            nodi.append(curve.data.shape[0]-1)
        else:
            pass
        return nodi

class opener(skeleton.prepare_opener):
    def check(self):
        with open(self.filename, encoding=ENCODING) as f:
            riga = f.readline()
        return riga.startswith('Date')

    def open(self,number=False):
        
        for pars in ['x','y','k']:
            self.curve.parameters[pars]=0
        self.curve.parameters['control']=None
        self.curve.parameters['version']='old'
        self.curve.parameters['SMDuration']=0.0
        
        self.parse()
        self.getData()
        
        if self.curve.parameters['version']=='old':
            self.getProtocols()
            self.createSegments('euristic')
        else:
            if self.curve.parameters['control']=='Peak Load Poking':
                self.getProtocols('poking')
                self.createSegments('poking')
            else:
                self.getProtocols()
                self.createSegments('safe')
        return self.curve
    
    def getProtocols(self,mode='all'):
        with open(self.filename, encoding=ENCODING) as f:
            if mode=='all':
                protocols=[]
                next = False
                for riga in f:
                    if riga.startswith('Profile') or riga.startswith('Piezo Indentation'):
                        next = True
                    elif next is True:
                        if riga.startswith('D'):
                            elements = riga.strip().split('\t')
                            protocols.append([float(elements[1]),float(elements[3])])
                        else:
                            break            
                self.curve.protocols = protocols
            elif mode=='poking':
                next = False
                for riga in f:
                    if riga.startswith('Profile') or riga.startswith('Piezo Indentation'):                    
                        next = True
                    elif next is True:
                        if riga.startswith('Max'):                        
                            elements = riga.strip().split('\t')
                            self.curve.parameters['max_load']=float(elements[1])*1e-6
                        elif riga.startswith('Piezo'):                        
                            elements = riga.strip().split('\t')
                            self.curve.parameters['piezo_speed']=float(elements[1])*1e-6
                        else:
                            break            
        
    def getData(self):
        with open(self.filename, encoding=ENCODING) as f:
            for riga in f:
                if riga.startswith('Time (s)'):
                    self.curve.channels = riga.strip().split('\t')
                    #Time (s)	Load (uN)	Indentation (nm)	Cantilever (nm)	Piezo (nm)	Auxiliary
                    self.multipliers = np.ones(len(self.curve.channels))
                    for i in range(len(self.curve.channels)):
                        if self.curve.channels[i].startswith('Time'):
                            self.curve.idTime = i
                        elif self.curve.channels[i].startswith('Load'):
                            self.curve.idForce = i
                        elif self.curve.channels[i].startswith('Piezo'):
                            self.curve.idZ = i
                        if 'nm' in self.curve.channels[i]:
                            self.multipliers[i]=1e-9
                        elif 'uN' in self.curve.channels[i] or 'µN' in self.curve.channels[i]:
                            self.multipliers[i]=1e-6
                    break
            data = []
            for riga in f:
                elements = riga.strip().split('\t')
                if len(elements) == len(self.curve.channels):
                    values = [float(x) for x in elements]
                    data.append(values)
        self.curve.data = np.array(data)*self.multipliers

    def createSegments(self,mode='safe'):
        nodi = getNodes(self.curve,mode)
        for i in range(len(nodi) - 1):
            if (nodi[i+1]-nodi[i])<2:
                continue
            self.curve.attach(self.curve.data[nodi[i]:nodi[i + 1],:])

    def parse(self):
        #specific parameters
        self.curve.parameters['SMDuration']=0.0

        with open(self.filename, encoding=ENCODING) as f:
            for riga in f:
                if riga.startswith('Time (s)'):
                    break
                if riga.startswith('Profile') or riga.startswith('Piezo Indentation'):
                    break
                if riga.startswith('X-position'):
                    coeff = 1.0
                    if 'um' in riga or 'µm' in riga:
                        coeff = 1e-6
                    self.curve.parameters['x']=coeff*float(riga.strip().split('\t')[1])
                elif riga.startswith('Y-position'):
                    coeff = 1.0
                    if 'um' in riga or 'µm' in riga:
                        coeff = 1e-6
                    self.curve.parameters['y']=coeff*float(riga.strip().split('\t')[1])
                elif riga.startswith('k (N/m)'):
                    self.curve.parameters['k']=float(riga.strip().split('\t')[1])
                elif riga.startswith('Tip radius'):
                    coeff = 1.0
                    if 'um' in riga or 'µm' in riga:
                        coeff = 1e-6
                    self.curve.tip['value']=coeff*float(riga.strip().split('\t')[1])
                elif riga.startswith('Control mode'):
                    self.curve.parameters['control']=riga.strip().split(':')[1].strip()
                elif riga.startswith('Measurement'):
                    self.curve.parameters['measurement']=riga.strip().split(':')[1].strip()
                elif riga.startswith('Software'):
                    self.curve.parameters['version']=riga.strip().split(':')[1].strip()
                elif riga.startswith('SMDuration'):
                    self.curve.parameters['SMDuration']=float(riga.strip().split(' ')[-1])