import os
import shutil
from fastapi.responses import FileResponse
import uvicorn
from fastapi import FastAPI, File, UploadFile

base_dir = '/tmp'

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

# Endpoint to read file
@app.get("/read_file")
async def read_file(file_name: str):
    try:
        readed_file = f'{base_dir}/data/{file_name}'
        data = None
        with open(readed_file, 'r') as f:
            data = f.read()
        return {'status': 'success', 'data': data}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# Endpoint to delete file
@app.get("/delete_file")
async def delete_file(file_name: str):
    try:
        deleted_file = f'{base_dir}/data/{file_name}'
        os.remove(deleted_file)
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    
# Endpoint to delete folder
@app.get("/delete_folder")
async def delete_folder(folder_name: str):
    try:
        deleted_folder = f'{base_dir}/{folder_name}'
        shutil.rmtree(deleted_folder)
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# Endpoint to get all files in folder
@app.get("/get_files")
async def get_files():
    try:
        files = os.listdir(base_dir)
        return {'status': 'success', 'data': files}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# Endpoint to upload file
@app.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...),
):
    try:
        contents = await file.read()
        with open(base_dir + '/data/' + file.filename, 'wb') as f:
            f.write(contents)
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# Endpoint to download file
@app.get("/download_file")
async def download_file(file_name: str):
    try:
        file_path = f'{base_dir}/data/{file_name}'
        return FileResponse(file_path, filename=file_name)
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)