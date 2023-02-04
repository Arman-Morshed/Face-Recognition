import asyncio
import aiohttp
import json
from FileManager import file_manager

class NetworkManager:
    def __init__(self, result):
        self.result = result

    async def handle_result(self, result):
       config = file_manager.get_configuration_file()
       url = f'{config.schema}://{config.host}/{config.endpoint}'
       payload = self.result.toJson()
       headers = {'Accept': 'application/json', 
                  'content-type': 'application/json'
                  }
       
       async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(payload), headers=headers) as res:
                print(res.status)
                
    def send_result(self):
        asyncio.run(self.handle_result(self.result))
                
