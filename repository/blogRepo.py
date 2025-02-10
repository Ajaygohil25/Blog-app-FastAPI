from datetime import datetime

from fastapi import HTTPException
from fastapi.openapi.models import Response
from sqlalchemy import select
from sqlalchemy.orm import join, aliased
from sqlalchemy.sql.functions import count, func
from starlette import status
from core.models import Blog, Images, Likes, Comments, Users
from core.schemas import BlogSchema, CommentResponse, BlogsResponse, ImageResponse
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
            for image in request.images:
                await upload_images(image.filename, blog_data.id,db)
        return {
                "details" : "Blog added successfully !",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def get_like_of_blog(blog_id, db, limit=None):
    """ This function get like of blog"""
    query = select(Users.name).select_from(
        join(Likes, Users, Likes.user_id == Users.id)
    ).where(Likes.blog_id == blog_id).limit(3)

    if limit is not None:
        query = query.limit(limit)

    liked_user_names = [row[0] for row in db.execute(query).all()]
    return liked_user_names

def get_image_of_blog(blog_id, db):
    """ This function get image of blog"""
    images = (select(Images.id,Images.image_name).
                  select_from(
                    join(Images, Blog, Images.blog_id == Blog.id)).
                  where(Images.blog_id == blog_id))
    images_data = []
    for i in db.execute(images).all():
        img_dict = ImageResponse(
                 id = i[0],
                image_url= f"/media/{i[1]}"
        )
        images_data.append(img_dict.__dict__)
    return images_data


def get_comment_of_blog(blog_id, db, limit=None):
    """ This function gets comments of a blog, with an optional limit on the number of comments."""
    user1 = aliased(Users)
    user2 = aliased(Users)

    comment_query = (
        select(
            Comments.id,
            user1.name.label("commented_by"),
            Comments.comment,
            user2.name.label("replied_by"),
            Comments.reply
        ).select_from(
            join(Comments, user1, Comments.commented_by == user1.id)
            .outerjoin(user2, Comments.reply_by == user2.id)
        )
        .where(Comments.blog_id == blog_id)
    )

    if limit is not None:
        comment_query = comment_query.limit(limit)

    comments_data = []
    for row in db.execute(comment_query).all():
        comment_dict = CommentResponse(
            id=row[0],
            commented_by=row[1],
            comment=row[2],
            reply_by=row[3] if row[3] is not None else None,  # Handle NULL `replied_by`
            reply=row[4] if row[4] is not None else None  # Handle NULL `reply`
        )
        comments_data.append(comment_dict.__dict__)
    return comments_data

def get_total_like_comment(blog_id,user_id, db):
    """ This function get total like and comment of blog"""
    total_like = (
        select(func.count(Likes.blog_id))
        .select_from(join(Likes, Blog, Likes.blog_id == Blog.id))
        .where(Likes.blog_id == blog_id)
    )
    total_like = db.execute(total_like).scalar()

    total_comment =  (
                    select(func.count(Comments.blog_id))
                    .select_from(join(Comments, Blog, Comments.blog_id == Blog.id))
                    .where(Comments.blog_id == blog_id)
    )
    total_comment = db.execute(total_comment).scalar()

    is_liked = db.query(Likes.user_id).filter(Likes.user_id == user_id , Likes.blog_id == blog_id).first()
    liked = False
    if is_liked:
        liked = True
    return total_like, total_comment, liked

def get_all_blog_data(user,db,page:int = 1, size:int = 5):
    """ This function get blog data with implementation pagination"""
    user_data = get_user(user.email, db)

    blog_query = db.query(Blog).order_by(Blog.created_at.desc())
    total_blogs = blog_query.count()
    blogs = blog_query.offset((page -1) * size).limit(size).all()

    blog_result = []
    for blog in blogs:
        total_like, total_comment, liked = get_total_like_comment(blog.id,user_data.id, db)
        blog_schema_obj = BlogsResponse(
            id = blog.id,
            title = blog.title,
            content = blog.content,
            created_at = blog.created_at,
            images = get_image_of_blog(blog.id, db),
            likes = get_like_of_blog(blog.id, db, 3),
            liked_by_you=liked,
            total_likes = total_like,
            view_all_likes= f"http://127.0.0.1:8000/blog/get-all-like/{blog.id}",
            comments = get_comment_of_blog(blog.id, db, 3),
            total_comments = total_comment,
            view_all_comments = f"http://127.0.0.1:8000/blog/get-all-comment/{blog.id}",
        )
        blog_result.append(blog_schema_obj.__dict__)
    next_page = f"/blog/show_all_blogs?page={page + 1}&size={size}" if (page * size) < total_blogs else None
    previous_page = f"/blog/show_all_blogs?page{page - 1}&size={size}" if page > 1  else None

    return {
        "blogs": blog_result,
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

def update_blog_data(blog_id: int, request_data: BlogSchema, response: Response, user,db):
    try:
        user_data = get_user(user.email, db)
        blog = check_blog_exist(blog_id, db)
        if not blog:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid blog ID"}

        if blog.user_id != user_data.id:
            raise HTTPException(status_code=500, detail="You can't update this blog post!")

        updated_data = request_data.model_dump(exclude_unset=True)
        updated_data = {key: value for key, value in updated_data.items() if not key.startswith('_')}
        db.query(Blog).filter(Blog.id == blog_id).update(updated_data)
        db.commit()
        return {"Message": "Blog data updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def delete_blog_data(blog_id: int,response: Response,user,db):
    try:
        user_data = get_user(user.email, db)
        blog = check_blog_exist(blog_id,db)
        if not blog:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"Error": "No data available or invalid blog ID"}

        if blog.user_id != user_data.id:
            raise HTTPException(status_code=500, detail="You can't delete this blog post!")

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

