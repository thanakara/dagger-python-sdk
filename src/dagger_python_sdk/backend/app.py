from typing import Annotated
from pathlib import Path

from fastapi import Depends, FastAPI, Request, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from dagger_python_sdk.sqlmodel import models
from dagger_python_sdk.backend.schemas import (
    PostCreate,
    UserCreate,
    PostResponse,
    UserResponse,
)
from dagger_python_sdk.sqlmodel.database import Base, engine, get_db

PACKAGE_DIR = Path("src") / "dagger_python_sdk"

# _________________Create-Tables__________________________/
Base.metadata.create_all(bind=engine)

# ________________Templates-Dir__________________________/
templates_dir = PACKAGE_DIR / "frontend" / "templates"
templates = Jinja2Templates(directory=templates_dir.as_posix())

# ________________Setup-FastAPI_________________________/
app = FastAPI()
app.mount(
    path="/static",
    app=StaticFiles(directory=PACKAGE_DIR / "frontend"),
    name="static",
)


@app.get("/", include_in_schema=False, name="home")
def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"title": "Home"}
    )


# ______________________Posts___________________________/
@app.get("/posts", include_in_schema=False, name="posts")
def posts_index(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="posts.html",
        context={"posts": posts, "title": "Home"},
    )


@app.get("/posts/{post_id}", include_in_schema=False)
def select_post(
    request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if post:
        title = post.title
        return templates.TemplateResponse(
            request=request,
            name="post.html",
            context={"post": post, "title": title},
        )
    raise HTTPException(
        status_code=status.HTTP_204_NO_CONTENT, detail="Post not found."
    )


# _____________________API\Users_______________________/
@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
# NOTE: Annotated is used for Dependency Injection
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.username == user.username)
    )
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists.",
        )

    result = db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists.",
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if user:
        return user
    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="User not found.")


@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    result = db.execute(
        select(models.Post).where(models.Post.user_id == user_id)
    )
    posts = result.scalars().all()
    return posts


@app.get(
    "/users/{user_id}/posts",
    response_model=list[PostResponse],
    name="all_user_posts",
)
def all_user_posts(
    request: Request, user_id: int, db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    result = db.execute(
        select(models.Post).where(models.Post.user_id == user_id)
    )
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request=request,
        name="user_posts.html",
        context={"posts": posts, "user": user},
    )


# _____________________API\Posts______________________/
@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts


@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == post.user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()

    if post:
        return post
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
    )


# ___________________Exception-Handler________________/
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(
    request: Request, exception: StarletteHTTPException
):
    message = (
        exception.detail
        if exception.detail
        else "An error occured. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code, content={"detail": message}
        )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


# ___________________Validation-Handler________________/
@app.exception_handler(RequestValidationError)
def validation_exception_handler(
    request: Request, exception: RequestValidationError
):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
