import logging
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi_pagination import add_pagination
from sqlalchemy.orm import Session
from starlette.responses import Response

from authentication.oauth2 import get_current_user
from core.database import get_db
from core.schemas import BlogSchema, TokenData, CommentSchema, ReplyComment
from repository.blogRepo import add_blog, get_all_blog_data, get_blog_data, update_blog_data, delete_blog_data, \
    like_unlike_post, comment_post, update_blog_comment, delete_blog_comment, reply_blog_comment, add_blog_image, \
    delete_blog_image, get_like_of_blog, get_comment_of_blog

router = APIRouter(
    tags=["Blogs"],
)
add_pagination(router)


logging.basicConfig(level=logging.DEBUG)
UPLOAD_FOLDER = Path("media")
@router.post("/blog/create_blog")
async def create_blog(
                title: str = Form(...),
                content: str = Form(...),
                images: Optional[List[UploadFile]] = File(None),
                current_user: TokenData  = Depends(get_current_user),
                db: Session = Depends(get_db)
):
    saved_files = []
    print("images here ", images)

    if images:
        for image in images:
            filepath = UPLOAD_FOLDER / image.filename
            with open(filepath, "wb") as image_file:
                shutil.copyfileobj(image.file, image_file)
            saved_files.append(str(filepath))
    print("files ", saved_files)
    request_data = BlogSchema(title=title, content=content, images=images)
    return await add_blog(request_data, current_user,db)

@router.get("/blog/show_all_blogs")
def get_all_blog(
                current_user: TokenData  = Depends(get_current_user),
                db: Session = Depends(get_db),
                 page:int = 1, size:int = 5):
    return get_all_blog_data(current_user,db, page, size)

@router.get("/blog/get_blog/{blog_id}")
def get_blog(blog_id: int,
             response: Response,
             db: Session = Depends(get_db)):
   return get_blog_data(blog_id, response, db)

@router.put("/blog/update_blog/{blog_id}")
def update_blog(blog_id: int, request_data: BlogSchema,
                response: Response,
                current_user: TokenData  = Depends(get_current_user),
                db: Session = Depends(get_db)):
    return update_blog_data(blog_id, request_data, response, current_user,db)

@router.delete("/blog/delete_blog/{blog_id}")
def delete_blog(blog_id: int,response: Response,
                current_user: TokenData  = Depends(get_current_user),
                db: Session = Depends(get_db)):

    return delete_blog_data(blog_id, response, current_user,db)

@router.post("/blog/like-unlike/{blog_id}")
def like_unlike(
        blog_id: int,
        response: Response,
        current_user: TokenData  = Depends(get_current_user),
        db: Session = Depends(get_db)):
    return like_unlike_post(db, response,current_user,blog_id)


@router.post("/blog/add-comment/{blog_id}", status_code= 200)
def add_comment(
        blog_id: int,
        request_data: CommentSchema,
        response: Response,
        current_user: TokenData  = Depends(get_current_user),
        db: Session = Depends(get_db)):
    return comment_post(db,request_data, response,current_user,blog_id)

@router.patch("/blog/update-comment/{comment_id}", status_code= 200)
def update_comment(
        comment_id : int,
        request_data: CommentSchema,
        response: Response,
        current_user: TokenData  = Depends(get_current_user),
        db: Session = Depends(get_db)):
    return update_blog_comment(db,request_data,response, current_user,comment_id)

@router.delete("/blog/delete-comment/{comment_id}", status_code= 200)
def delete_comment(
        comment_id : int,
        response: Response,
        current_user: TokenData  = Depends(get_current_user),
        db: Session = Depends(get_db)):
    return delete_blog_comment(db, response,current_user,comment_id)

@router.patch("/blog/reply-comment/{comment_id}", status_code= 200)
def reply_comment(
        comment_id : int,
        request_data: ReplyComment,
        response: Response,
        current_user: TokenData = Depends(get_current_user),
        db: Session = Depends(get_db)):
    return reply_blog_comment(comment_id,request_data,response, current_user, db)

@router.delete("/blog/delete-blog-image/")
def delete_image(blog_id: int, image_id: int,
                 response: Response,
                 current_user: TokenData = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    return delete_blog_image(blog_id, image_id, response, current_user, db)

@router.post("/blog/update-blog-image/{blog_id}")
async def update_blog_image(blog_id: int,
                        response: Response,
                        images: List[UploadFile] = File(None),
                        current_user: TokenData = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    saved_files = []
    if images:
        for image in images:
            filepath = UPLOAD_FOLDER / image.filename
            with open(filepath, "wb") as image_file:
                shutil.copyfileobj(image.file, image_file)
            saved_files.append(str(filepath))
    print("files ", saved_files)
    return await add_blog_image(blog_id, images, response,current_user, db)

@router.get("/blog/get-all-like/{blog_id}")
def get_all_like(blog_id: int, response: Response, db: Session = Depends(get_db)):
    return get_like_of_blog(blog_id, db)

@router.get("/blog/get-all-comment/{blog_id}")
def get_all_like(blog_id: int, response: Response, db: Session = Depends(get_db)):
    return get_comment_of_blog(blog_id, db)