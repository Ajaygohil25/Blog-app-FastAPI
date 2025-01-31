from datetime import datetime
from fastapi import HTTPException
from fastapi.openapi.models import Response
from starlette import status
from core.models import Blog
from core.schemas import Blog_schema
from repository.userRepo import get_user


def add_blog(request: Blog_schema,user_email_id, db):
    """ This insert blog data into database"""
    user_data = get_user(user_email_id, db)
    try:
        blog_data = Blog(
            title = request.title,
            content = request.content,
            user_id = user_data.id,
            created_at = datetime.now()
        )
        db.add(blog_data)
        db.commit()
        db.refresh(blog_data)
        return {
                "details" : "Blog added successfully !",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def get_all_blog_data(db, page:int = 1, size:int = 5):
    """ This function get blog data with implementation pagination"""
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

def get_blog_data(blog_id: int, response: Response, db):
    try:
        blog = db.query(Blog).filter(Blog.id == blog_id).first()
        if not blog:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid ID"}
        return blog
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def update_blog_data(blog_id: int, request_data: Blog_schema, response: Response, db):
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

def delete_blog_data(blog_id: int,response: Response,db):
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
