from datetime import datetime

from fastapi import HTTPException
from fastapi.openapi.models import Response
from starlette import status
from core.models import Blog, Images, Likes, Comments
from core.schemas import BlogSchema
from repository.userRepo import get_user

async def upload_images(image, blog_id,db):
    """ This function upload image into database"""
    image_data = Images(
                image_name = image,
                blog_id = blog_id,
    )
    db.add(image_data)
    db.commit()
    db.refresh(image_data)


async def add_blog(request: BlogSchema,user, db):
    """ This insert blog data into database"""
    print("user",user)
    user_data = get_user(user.email, db)
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
        if request.images:
            print("Images here")
            for image in request.images:
                await upload_images(image.filename, blog_data.id,db)
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
    next_page = f"/blog/show_all_blogs?page={page + 1}&size={size}" if (page * size) < total_blogs else None
    previous_page = f"/blog/show_all_blogs?page{page - 1}&size={size}" if page > 1  else None

    return {
        "blogs": blogs,
        "total_blogs": total_blogs,
        "next_page": next_page,
        "previous_page": previous_page
    }

def check_blog_exist(blog_id: int, db):
    """ This function check blog exist or not"""
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        return None
    return blog

def get_blog_data(blog_id: int, response: Response, db):
    try:
        blog = check_blog_exist(blog_id, db)
        if not blog:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid ID"}
        return blog
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def update_blog_data(blog_id: int, request_data: BlogSchema, response: Response, db):
    try:
        blog = check_blog_exist(blog_id, db)
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
        blog = check_blog_exist(blog_id,db)
        if not blog:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid ID"}
        db.delete(blog)
        db.commit()
        return {"Message": "Blog deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def like_unlike_post(db, response,user,blog_id: int):
    try:
        user_data = get_user(user.email, db)
        blog = check_blog_exist(blog_id, db)

        if not blog:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid ID"}

        is_liked = db.query(Likes).filter(Likes.user_id == user_data.id , Likes.blog_id == blog_id).first()
        if is_liked:
            db.delete(is_liked)
            db.commit()
            return {"Message": "Blog post unliked successfully"}
        else:
            like_data = Likes(user_id = user_data.id, blog_id = blog_id)
            db.add(like_data)
            db.commit()
            db.refresh(like_data)
        return {"Message": "Blog post liked successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

async def add_blog_image(blog_id,images, response,current_user,db):
    """ This function add blog image into existing blog data in database"""
    blog_data = check_blog_exist(blog_id, db)
    user_data = get_user(current_user.email, db)

    if not blog_data:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": "No data available or invalid ID"}

    if blog_data.user_id != user_data.id:
        raise HTTPException(status_code=500, detail="You can't add image to this blog post!")

    if images:
        for image in images:
            await upload_images(image.filename, blog_data.id, db)
    return {
        "details": "Image uploaded successfully !",
    }

def delete_blog_image(blog_id,image_id,response,current_user,db):
    blog_data = check_blog_exist(blog_id, db)
    user_data = get_user(current_user.email, db)

    if not blog_data:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": "No data available or invalid Blog ID"}

    if blog_data.user_id != user_data.id:
        raise HTTPException(status_code=500, detail="You can't delete the image of this blog post!")

    image = db.query(Images).filter(Images.id == image_id).first()
    if not image:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": "No data available or invalid Image ID"}

    if image.blog_id != blog_id:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Error": "invalid Blog ID"}
    db.delete(image)
    db.commit()
    return {"Message": "Blog deleted successfully"}

def comment_post(db,request_data, response,current_user,blog_id):
    try:
        user_data = get_user(current_user.email, db)
        blog = check_blog_exist(blog_id, db)
        if not blog:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid ID"}

        add_comment = Comments(comment = request_data.comment, commented_by = user_data.id, blog_id = blog_id)
        db.add(add_comment)
        db.commit()
        db.refresh(add_comment)
        return {"Message": "Comment added successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def check_comment_exist(comment_id: int,response: Response, db):
    """ This function check comment exist or not"""
    comment = db.query(Comments).filter(Comments.id == comment_id).first()
    print("comment",comment)
    if not comment:
        return None
    return comment

def update_blog_comment(db,request_data, response,current_user,comment_id):
    """ This function update the comment of blog"""
    try:
        user_data = get_user(current_user.email, db)
        comment_data = check_comment_exist(comment_id, response,db)
        if not comment_data:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid comment data ID"}

        if comment_data.commented_by != user_data.id:
            raise HTTPException(status_code=500, detail="You can't update this comment")
        comment_data.comment = request_data.comment
        db.commit()
        db.refresh(comment_data)
        return {"Message": "Comment updated successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def delete_blog_comment(db, response,current_user,comment_id):
    """ This function delete the blog comment"""
    try:
        user_data = get_user(current_user.email, db)
        comment_data = check_comment_exist(comment_id, response, db)
        if not comment_data:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid comment data ID"}

        if comment_data.commented_by != user_data.id:
            raise HTTPException(status_code=500, detail="You can't delete this comment")
        db.delete(comment_data)
        db.commit()
        return {"Message": "Comment deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def reply_blog_comment(comment_id,request_data, response,current_user, db):
    try:
        user_data = get_user(current_user.email, db)
        comment_data = check_comment_exist(comment_id, response, db)
        if not comment_data:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid comment data ID"}

        comment_data.reply = request_data.reply
        comment_data.reply_by = user_data.id
        db.commit()
        db.refresh(comment_data)
        return {"Message": "Reply added successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

