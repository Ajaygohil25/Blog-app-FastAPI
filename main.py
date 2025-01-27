from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List
from starlette import status
from starlette.responses import Response
from database import engine, get_db
from schemas import Blog_schema
from models import Base, Blog
from datetime import datetime


app = FastAPI()

Base.metadata.create_all(engine)

# Create blog
@app.post("/blog/create_blog", tags=["Blog"])
def create_blog(request: Blog_schema, db: Session = Depends(get_db)):
    try:
        blog_data = Blog(
            title = request.title,
            content = request.content,
            created_at = datetime.now()
        )
        db.add(blog_data)
        db.commit()
        db.refresh(blog_data)
        return {
                "details" : "Blog added successfully !",
                "Blog data": blog_data
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Get all blog data
@app.get("/blog/get_all_blog", response_model=List[Blog_schema], tags=["Blog"])
def get_all_blogs(response: Response, db: Session = Depends(get_db)):
    try:
        blogs = db.query(Blog).all()
        if not blogs:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available"}
        return blogs
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Get blog with particular ID
@app.get("/blog/get_blog/{blog_id}", tags=["Blog"])
def get_blog(blog_id: int,response: Response, db: Session = Depends(get_db)):
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid ID"}
        return blog
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.delete("/blog/delete_blog/{blog_id}", tags=["Blog"])
def delete_blog(blog_id: int,response: Response,db: Session = Depends(get_db)):
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid ID"}
        db.delete(blog)
        db.commit()
        return {"Message": "Blog deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.put("/blog/update_blog/{blog_id}", tags=["Blog"])
def update_blog(blog_id: int, request_data: Blog_schema, response: Response, db: Session = Depends(get_db)):
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid ID"}
        updated_data = request_data.model_dump(exclude_unset=True)
        updated_data = {key: value for key, value in updated_data.items() if not key.startswith('_')}
        db.query(Blog).filter(Blog.id == blog_id).update(updated_data)
        db.commit()
        return {"Message": "Blog data updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
