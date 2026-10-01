import requests
from flask import Flask

app = Flask(__name__)
app.json.ensure_ascii = False
GENERAL_URL = "http://127.0.0.1:5100"


@app.get("/posts/<int:post_id>")
def get_post(post_id):
    try:
        response = requests.get(f"{GENERAL_URL}/posts/{post_id}", timeout=3)
    except requests.Timeout:
        return {"error": "일반 서비스의 응답이 늦습니다."}, 504
    except requests.ConnectionError:
        return {"error": "일반 서비스에 연결할 수 없습니다."}, 502
    return response.json(), response.status_code


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5200)
