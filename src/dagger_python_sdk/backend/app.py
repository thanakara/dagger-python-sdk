import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

PACKAGE_DIR = Path("src") / "dagger_python_sdk"

# _______Load-Posts____________________________/
jsonpath = PACKAGE_DIR.parent / "data" / "posts.json"
with jsonpath.open("r") as f_:
    posts: list[dict] = json.load(f_)

# _______Templates-Dir________________________/
templates_dir = PACKAGE_DIR / "frontend" / "templates"
templates = Jinja2Templates(directory=templates_dir.as_posix())

# ______Setup-FastAPI_________________________/
app = FastAPI()
app.mount(
    path="/static",
    app=StaticFiles(directory=PACKAGE_DIR / "frontend" / "css"),
    name="static",
)


@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="home.html", context={"title": "Home"}
    )


# ______________________Posts___________________________/
@app.get("/posts", include_in_schema=False)
def posts_index(request: Request):
    return templates.TemplateResponse(
        request=request, name="posts.html", context={"posts": posts, "title": "Posts"}
    )


@app.get("/posts/{post_id}", include_in_schema=False)
def select_post(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return templates.TemplateResponse(
                request=request,
                name="post.html",
                context={"post": post, "title": post["title"]},
            )
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found")


# _____________________API\Posts______________________/
@app.get("/api/posts")
def get_posts():
    return posts


@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found")


# ___________________Exception-Handler________________/
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
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
def validation_exception_handler(request: Request, exception: RequestValidationError):
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
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
