import json

def emptyCurve():
    curve = {
        "filename": "noname",
        "date": "2021-12-02",
        "device_manufacturer": "Optics11",
        "tip":{
            "geometry": "sphere",
            "radius": 0.0,
            "angle": 0.0
        },
        "spring_constant": 0.0, 
		"segment": "approach",
        "speed": 0.0,
        "data":{
            "F":[],
            "Z":[]
        }
    }
    return curve


class saveJSON(object):
    def __init__(self,fname) -> None:
        self.filename = fname
        self.selectedsegment = 0
        self.curves = []
        
    def addCurve(self, curve):
        geometry = curve.tip['geometry']
        tip_value = curve.tip['value']
        spring = curve.parameters['k']

        cv = emptyCurve()
        cv['filename'] = self.filename.name
        if geometry in ('sphere', 'cylinder'):
            cv['tip']['radius'] = tip_value
        else:
            cv['tip']['angle'] = tip_value
        cv['tip']['geometry'] = geometry
        cv['spring_constant']=spring
        cv['position']=(curve.parameters['x'],curve.parameters['y'])
        z,f=curve.segments[self.selectedsegment].getCurve()
        cv['data']['Z']=list(z)                
        cv['data']['F']=list(f)
        self.curves.append(cv)

    def setSegment(self, number):
        self.selectedsegment = number
        
    def save(self):
        exp = {'Description':'Optics11 data'}
        pro = {}
        json.dump({'experiment':exp,'protocol':pro,'curves':self.curves},open(self.filename,'w'))