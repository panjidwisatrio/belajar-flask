import sys
import os
import uvicorn
from fastapi import FastAPI

base_dir = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Automate Preventive Maintenance API", version="1.0", )

# Endpoint to create folder and file
@app.get("/create_folder_file")
async def create_folder_file():
    try:
        data = None
        os.mkdir(base_dir + '/data')
        with open(base_dir + '/data/test.txt', 'w') as f:
            f.write('Hello World!')
            
        with open(base_dir + '/data/test.txt', 'r') as f:
            data = f.read()
        return {'status': 'success', 'data': data}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)