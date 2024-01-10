from fastapi import APIRouter, Depends, HTTPException, status
from databases import Database
from sqlalchemy import select, insert, update, delete, desc
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
import random, os, shutil

# import local modules
from app.core import database_connections as DBC, configs as CF

router = APIRouter()

class Project(BaseModel):
    name: str
    pic: str
    
class GetProjectOut(BaseModel):
    id: int = 0
    name: str = "example_project_name"
    pic: str = "example_pic"
    container_name: str = "example_container_name"
    created_date: object

class PostProjectOut(BaseModel):
    message: str = "Project created successfully"

class PatchProjectOut(BaseModel):
    message: str = "Project updated successfully"

class DeleteProjectOut(BaseModel):
    message: str = "Project deleted successfully"

def _generate_container_name(project_name, project_pic):
    result = f"{project_name.lower().strip().replace(' ', '')}{project_pic.lower().strip().replace(' ', '')}-{random.randint(1000, 9999)}"
    
    return result

@router.get(
    "/project",
    status_code=status.HTTP_200_OK,
    response_model=list[GetProjectOut],
    summary="Retrieve all projects",
    description="Fetches a list of all projects ordered by creation date. Returns an empty list if no projects are found."
)
async def retrieve_project(db: Database = Depends(DBC.get_db)):
    query = select(DBC.projects_table).order_by(desc(DBC.projects_table.c.created_date))
    projects = await db.fetch_all(query)
    
    # Check if the projects list is empty and return a message
    if not projects:
        return {"message": "No projects found"}
    
    return projects


@router.post(
    "/project",
    status_code=status.HTTP_201_CREATED,
    response_model=PostProjectOut,
    summary="Create a new project",
    description="Creates a new project with the provided details and automatically generates a container blob storage with unique name."
)
async def create_project(project: Project, db: Database = Depends(DBC.get_db)):
    # Dump the project model and generate the container name
    project_data = project.model_dump()
    project_data['container_name'] = _generate_container_name(project_data['name'], project_data['pic'])

    # TODO: Create the container
    try:
        os.mkdir(f"{CF.BASE_DIR}/projects/{project_data['container_name']}")
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create container. Error: {str(error)}")

    # Insert the project into the database
    try:
        query = insert(DBC.projects_table).values(**project_data)
        project_id = await db.execute(query)
        return {"message": "Project created successfully", "project_id": project_id}
    except SQLAlchemyError as error:
        # Rollback any changes made if there's an error
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create project. Error: {str(error)}")


@router.patch(
    "/project/{id}",
    status_code=status.HTTP_200_OK,
    response_model=PatchProjectOut,
    summary="Update an existing project",
    description="Updates the details of an existing project identified by its ID."
)
async def update_project(id: int, project: Project, db: Database = Depends(DBC.get_db)):
    # Check if the project with the given ID exists
    select_query = select(DBC.projects_table).where(DBC.projects_table.c.id == id)
    project_exists = await db.fetch_one(select_query)
    
    if project_exists:
        try:
            # If the project exists, proceed with the update
            update_query = update(DBC.projects_table).where(DBC.projects_table.c.id == id).values(**project.model_dump())
            await db.execute(update_query)
            return {"message": "Project updated successfully"}
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update project. Error: {str(error)}")
    else:
        # If the project does not exist, return a 404 error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


@router.delete(
    "/project/{id}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteProjectOut,
    summary="Delete an existing project",
    description="Deletes an existing project identified by its ID from the database."
)
async def delete_project(id: int, db: Database = Depends(DBC.get_db)):
    # Check if the project with the given ID exists
    select_query = select(DBC.projects_table).where(DBC.projects_table.c.id == id)
    project_exists = await db.fetch_one(select_query)
    
    if project_exists:
        # TODO: Delete Container
        try:
            # Check is project exists
            if not os.path.exists(f"{CF.BASE_DIR}/projects/{project_exists['container_name']}"):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")
            
            shutil.rmtree(f"{CF.BASE_DIR}/projects/{project_exists['container_name']}")
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to delete container. Error: {str(error)}")
        
        # If the project exists, proceed with the delete operation
        delete_query = delete(DBC.projects_table).where(DBC.projects_table.c.id == id)
        await db.execute(delete_query)
        return {"message": "Project deleted successfully"}
    else:
        # If the project does not exist, return a 404 error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
