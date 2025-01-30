from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List
from starlette import status
from starlette.responses import Response

import mail
from Profile_Management import users
from database import engine, get_db
from schemas import Blog_schema
from models import Base, Blog
from datetime import datetime
from fastapi_pagination import Page, add_pagination, LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate

app = FastAPI()
app.include_router(users.router)
add_pagination(app)
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


# api with pagination
# Use of pagination with library of fastapi_pagination
@app.get("/blog/all_blog", response_model = LimitOffsetPage[Blog_schema], tags = ["Pagination"])
def get_all_blogs(response: Response, db: Session = Depends(get_db)):
    try:
        blogs = db.query(Blog).all()
        if not blogs:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available"}
        return paginate(db.query(Blog).order_by(Blog.created_at.desc()))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Create a custom pagination
@app.get("/blog/all_blogs", tags = ["Pagination"])
def get_all_blog(db: Session = Depends(get_db), page:int = 1, size:int = 5):
    blog_query = db.query(Blog).order_by(Blog.created_at.desc())
    total_blogs = blog_query.count()
    blogs = blog_query.offset((page -1) * size).limit(size).all()

    next_page = f"/blog/all_blogs?page={page + 1}&size={size}" if (page * size) < total_blogs else None
    previous_page = f"/blog/all_blogs?page{page - 1}&size={size}" if page > 1  else None

    return {
        "blogs": blogs,
        "total_blogs": total_blogs,
        "next_page": next_page,
        "previous_page": previous_page
    }

@app.post("/testp_mail")
async def testp_mail():
    await mail.send_mail("pharmfast2022@gmail.com", "login", "Login success yee yee")


