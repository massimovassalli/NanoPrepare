import os

tips = {
    'sphere':{'geometry':'sphere','parameter':'Radius','unit':'um','value':0.0},
    'cylinder':{'geometry':'cylinder','parameter':'Radius','unit':'um','value':0.0},
    'cone':{'geometry':'cone','parameter':'Angle','unit':'deg','value':0.0},
    'pyramid':{'geometry':'pyramid','parameter':'Angle','unit':'deg','value':0.0},
    'other':{'geometry':'other','parameter':'Unknown','unit':'au','value':0.0}
}

class segment(object):
    def __init__(self,parent):
        self.curve=parent
        self.data = None
        self.idTime=None
        self.idForce=None
        self.idZ = None
        self.isDeflection=False
        self.value = None #see below
        self.mode = None #speed = constant [speed], +values for approach; 
                         #pause = constant [position] ; force = constant [force] ;
                         #sineZ = sine controlling position [freq]; sineF = sine controlling force [freq]
        self.channels=[]

    def getCurve(self,mode='FZ'):
        if mode == 'FZ':
            force = self.data[:,self.idForce].copy()
            if self.isDeflection:
                force = force * self.curve.parameters['k']
            return self.data[:,self.idZ],force
        elif mode == 'FT':
            force = self.data[:,self.idForce].copy()
            if self.isDeflection:
                force = force * self.curve.parameters['k']
            return self.data[:,self.idTime],force

class curve(object):
    def __init__(self,file_path=None) -> None:
        self.filename = file_path
        self.dir , self.basename = os.path.split(file_path)
        self.data = None
        self.tip = tips['sphere']
        self.parameters={'k':None,'x':None,'y':None}
        self.idTime=None
        self.idForce=None
        self.idZ = None
        self.isDeflection=False        
        self.channels=[]
        self.segments=[]
        
    def parse(self):
        return

    def attach(self,data):
        s = segment(self)
        s.idTime = self.idTime
        s.idForce = self.idForce
        s.idZ = self.idZ
        s.isDeflection = self.isDeflection
        s.data=data
        self.segments.append(s)
        
    def getTimeForce(self):
        return self.data[:,self.idTime],self.data[:,self.idForce]

class prepare_opener(object):
    def __init__(self,file_path) -> None:
        self.filename = file_path
        self.dir , self.basename = os.path.split(file_path)
        self.curve=curve(file_path)
        
    def isMultiple(self):
        return False
        
    def check(self):
        return True
    
    def open(self):
        self.parse()
        return self.curve