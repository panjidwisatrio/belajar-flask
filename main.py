import sys
import uvicorn
from fastapi import FastAPI

from app.api import project_router, upload_file_router

app = FastAPI(title="Automate Preventive Maintenance API", version="1.0", )

app.include_router(project_router.router, tags=["project"])
app.include_router(upload_file_router.router, tags=["upload_file"])

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
    