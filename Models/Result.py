class Result:
    def __init__(self, name, verified):
        self._name = name
        self._verified = verified
    
    @property
    def name(self):
        return self._name
    
    @property
    def verified(self):
        return self._verified
    
    @name.setter
    def name(self, name):
        self._name= name
        
    @verified.setter
    def verified(self, verified):
        self._verified = verified
        
    
    def toJson(self):
        return {'name': self._name, 'verified': self._verified}