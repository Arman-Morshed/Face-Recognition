class Configuration:
    def __init__(self, schema, endpoint, host):
        self._schema = schema
        self._endpoint = endpoint
        self._host = host
        
    
    @property
    def schema(self):
        return self._schema
    
    @property
    def endpoint(self):
        return self._endpoint
    
    @property
    def host(self):
        return self._host
    
    
    @schema.setter
    def schema(self, schema):
        self._schema = schema
        
    @endpoint.setter
    def endpoint(self, endpoint):
        self._endpoint = endpoint
        
    @host.setter
    def host(self, host):
        self._host = host    
            