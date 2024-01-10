from typing import List
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, status, UploadFile
from zipfile import ZipFile
from databases import Database
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import select
from magic import Magic
from app.core import database_connections as DBC, configs as CF
import os

router = APIRouter()

class  FileRequest(BaseModel):
    project_id: int
    device_type: str
    
class DeleteFileRequest(BaseModel):
    project_id: int
    log_name: List[str]

class FileResult(BaseModel):
    status_code: int = status.HTTP_200_OK
    detail: List[str]

class DeleteFileResult(BaseModel):
    status_code: int = status.HTTP_200_OK
    detail: str

@router.post(
    "/uploadfile/", 
    status_code=status.HTTP_200_OK, 
    response_model=FileResult,
    summary="Upload file to blob storage",
    description="Upload file to blob storage by container id and device type, return file name and blob sas url"
)
async def upload_file(
    project_id: int = Form(...),
    device_type: str = Form(...),
    file: UploadFile = File(...), 
    db: Database = Depends(DBC.get_db)
):
    # Check if file is an zip file
    if file.content_type != "application/x-zip-compressed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File is not an zip file, content type is {file.content_type}")
    
    # TODO: Get container_name from database
    query = select(DBC.projects_table.c.container_name).where(DBC.projects_table.c.id == project_id)
    container_name = await db.fetch_one(query)
    
    if container_name == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")
    
    # Create a checker
    checker = Magic(mime=True)
    
    # list of file uploaded
    files = []
    
    # Extract file name from path
    try:
        with ZipFile(file.file, "r") as zip:
            # Upload every file in zip
            for name in zip.namelist():
                file_content = zip.read(name)[4096:]
                # Check every file in zip, is it readable?
                if checker.from_buffer(file_content) != "text/plain":
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File {name} in zip is not readable")
            
            # TODO:  Upload every file in zip
            for name in zip.namelist():
                contents = zip.read(name)
                file_name = f"{CF.BASE_DIR}/projects/{container_name['container_name']}/logs/{device_type}/{name}"
                with open(file_name, "wb") as f:
                    f.write(contents)
                files.append(file_name)
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to upload file. Error: {str(error)}")
       
    # Return file name and blob sas url
    return HTTPException(status_code=status.HTTP_200_OK, detail=files)

@router.post(
    "/getfile/", 
    status_code=status.HTTP_200_OK, 
    response_model=FileResult,
    summary="Get file from blob storage",
    description="Get file from blob storage by container id and device type, return file name and blob sas url"
)
async def get_file(item: FileRequest, db: Database = Depends(DBC.get_db)):
    # TODO: Get container_name from database
    query = select(DBC.projects_table.c.container_name).where(DBC.projects_table.c.id == item.project_id)
    container_name = await db.fetch_one(query)
    
    if container_name == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")
    
    # list of file uploaded
    files = []
    
    # TODO: Get all logs in container
    for root, dirs, files in os.walk(f"{CF.BASE_DIR}/projects/{container_name['container_name']}/logs/{item.device_type}"):
        for file in files:
            files.append(f"{root}/{file}")
    
    # Return file name and blob sas url
    return HTTPException(status_code=status.HTTP_200_OK, detail=files, headers={"X-Total-Count": str(len(files))})

@router.delete(
    "/deletefile/", 
    status_code=status.HTTP_200_OK, 
    response_model=DeleteFileResult,
    summary="Delete file from blob storage",
    description="Delete file from blob storage by container id and blob name"
)
async def delete_file(item: DeleteFileRequest, db: Database = Depends(DBC.get_db)):
    # TODO: Get container_name from database
    query = select(DBC.projects_table.c.container_name).where(DBC.projects_table.c.id == item.project_id)
    container_name = await db.fetch_one(query)
    
    if container_name == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")
  
    # TODO: Delete log
    for log in item.log_name:
        try:
            os.remove(f"{CF.BASE_DIR}/projects/{container_name['container_name']}/logs/{item.device_type}/{log}")
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to delete log. Error: {str(error)}")
    
    # Return file name and blob sas url
    return HTTPException(status_code=status.HTTP_200_OK, detail="Blob deleted successfully")