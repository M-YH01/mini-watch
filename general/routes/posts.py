import psycopg
from flask import Blueprint, render_template, request, redirect, url_for

from post_rules import clean_title_body, validate_post
from repositories import posts as posts_repo

bp = Blueprint("posts", __name__)


@bp.get("/")
def index():
    try:
        posts = posts_repo.list_posts()
    except psycopg.Error:
        return render_template("error.html", message="게시글을 불러올 수 없습니다."), 503
    return render_template("index.html", posts=posts)


@bp.get("/board/<int:post_id>")
def detail(post_id):
    post = posts_repo.find_post(post_id)
    if post is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
    return render_template("detail.html", post=post)


@bp.route("/board/new", methods=["GET", "POST"])
def new_post():
    if request.method == "GET":
        return render_template("new.html", title="", body="", error=None)

    title, body = clean_title_body(request.form)
    error = validate_post(title, body)
    if error:
        return render_template("new.html", title=title, body=body, error=error), 400

    post_id = posts_repo.create_post(title, body)
    return redirect(url_for("posts.detail", post_id=post_id), code=303)


@bp.route("/board/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    post = posts_repo.find_post(post_id)
    if post is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404

    if request.method == "GET":
        return render_template(
            "edit.html", post_id=post_id, title=post["title"], body=post["body"], error=None
        )

    title, body = clean_title_body(request.form)
    error = validate_post(title, body)
    if error:
        return render_template(
            "edit.html", post_id=post_id, title=title, body=body, error=error
        ), 400

    updated = posts_repo.update_post(post_id, title, body)
    if updated is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
    return redirect(url_for("posts.detail", post_id=post_id), code=303)


@bp.route("/board/<int:post_id>/delete", methods=["GET", "POST"])
def delete_post(post_id):
    post = posts_repo.find_post(post_id)
    if post is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404

    if request.method == "GET":
        return render_template("delete.html", post=post)

    deleted = posts_repo.delete_post(post_id)
    if deleted is None:
        return render_template("error.html", message="게시글을 찾을 수 없습니다."), 404
    return redirect(url_for("posts.index"), code=303)
