from flask import Flask

app = Flask(__name__)
app.json.ensure_ascii = False

posts = {
    1: {"id": 1, "title": "첫 번째 공지", "body": "새 프로젝트를 시작합니다."},
    2: {"id": 2, "title": "실습 안내", "body": "게시글 번호를 바꿔 보세요."},
}


@app.get("/posts/<int:post_id>")
def get_post(post_id):
    if post_id not in posts:
        return {"error": "게시글을 찾을 수 없습니다."}, 404
    return posts[post_id]


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5100)
