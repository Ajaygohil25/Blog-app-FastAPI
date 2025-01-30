from fastapi import APIRouter, Depends
from fastapi_pagination import add_pagination
from sqlalchemy.orm import Session
from starlette.responses import Response

from authentication.oauth2 import get_current_user
from core.database import get_db
from core.schemas import Blog_schema, TokenData
from repository.blogRepo import add_blog, get_all_blog_data, get_blog_data, update_blog_data, delete_blog_data

router = APIRouter(
    tags=["Blogs"],
)
add_pagination(router)
@router.post("/blog/create_blog")
def create_blog(request: Blog_schema, current_user: TokenData  = Depends(get_current_user),db: Session = Depends(get_db)):
    return add_blog(request, db)

@router.get("/blog/all_blogs")
def get_all_blog(db: Session = Depends(get_db), page:int = 1, size:int = 5):
    return get_all_blog_data(db, page, size)

@router.get("/blog/get_blog/{blog_id}")
def get_blog(blog_id: int, response: Response, db: Session = Depends(get_db)):
   return get_blog_data(blog_id, response, db)

@router.put("/blog/update_blog/{blog_id}")
def update_blog(blog_id: int, request_data: Blog_schema, response: Response, db: Session = Depends(get_db)):
    return update_blog_data(blog_id, request_data, response, db)

@router.delete("/blog/delete_blog/{blog_id}")
def delete_blog(blog_id: int,response: Response,db: Session = Depends(get_db)):
    return delete_blog_data(blog_id, response, db)

# api with pagination
# Use of pagination with library of fastapi_pagination
# @app.get("/blog/all_blog", response_model = LimitOffsetPage[Blog_schema], tags = ["Pagination"])
# def get_all_blogs(response: Response, db: Session = Depends(get_db)):
#     try:
#         blogs = db.query(Blog).all()
#         if not blogs:
#             response.status_code = status.HTTP_404_NOT_FOUND
#             return {"Error": "No data available"}
#         return paginate(db.query(Blog).order_by(Blog.created_at.desc()))
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")