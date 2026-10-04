import uvicorn
from .config import Settings
if __name__=='__main__':
    config=Settings()
    uvicorn.run('api.main:app',host=config.host,port=config.port,log_level=config.logging_level.lower(),access_log=False,proxy_headers=False)
