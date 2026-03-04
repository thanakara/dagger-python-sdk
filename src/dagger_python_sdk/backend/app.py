import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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


@app.get("/posts", include_in_schema=False)
def posts_index(request: Request):
    return templates.TemplateResponse(
        request=request, name="posts.html", context={"posts": posts, "title": "Posts"}
    )


@app.get("/api/posts")
def get_posts():
    return posts
