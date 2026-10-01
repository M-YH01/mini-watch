import requests
import psycopg
from db import connect_db
from flask import Flask, Response, request

app = Flask(__name__)
app.json.ensure_ascii = False
GENERAL_URL = "http://127.0.0.1:5100"


def record_event(method, path, status):
    if status in (502, 504):
        event_type = "upstream_error"
    elif path == "/auth/login" and status == 200:
        event_type = "login_success"
    elif path == "/auth/login" and status == 401:
        event_type = "login_failure"
    else:
        event_type = "http_request"

    try:
        with connect_db() as conn:
            conn.execute(
                """INSERT INTO http_events (method, path, status_code, event_type)
                   VALUES (%s, %s, %s, %s)""",
                (method, path, status, event_type),
            )
    except psycopg.Error:
        app.logger.warning("감시 DB에 요청 기록을 저장하지 못했습니다.")


def forward(method, path):
    try:
        upstream = requests.request(
            method,
            f"{GENERAL_URL}{path}",
            json=request.get_json(silent=True),
            cookies=request.cookies,
            timeout=3,
            allow_redirects=False,
        )
    except requests.Timeout:
        record_event(method, path, 504)
        return {"error": "일반 서비스의 응답이 늦습니다."}, 504
    except requests.ConnectionError:
        record_event(method, path, 502)
        return {"error": "일반 서비스에 연결할 수 없습니다."}, 502

    response = Response(
        upstream.content,
        status=upstream.status_code,
        content_type=upstream.headers.get("Content-Type", "application/octet-stream"),
    )
    for cookie in upstream.raw.headers.getlist("Set-Cookie"):
        response.headers.add("Set-Cookie", cookie)
    record_event(method, path, upstream.status_code)
    return response


@app.get("/posts/<int:post_id>")
def get_post(post_id):
    return forward("GET", f"/posts/{post_id}")


@app.post("/auth/login")
def login():
    return forward("POST", "/auth/login")


@app.post("/auth/logout")
def logout():
    return forward("POST", "/auth/logout")


@app.get("/api/events")
def get_events():
    event_type = request.args.get("event_type")
    allowed = {"login_success", "login_failure", "upstream_error", "http_request"}
    if event_type is not None and event_type not in allowed:
        return {"error": "지원하지 않는 이벤트 종류입니다."}, 400

    try:
        with connect_db() as conn:
            if event_type is None:
                rows = conn.execute(
                    "SELECT * FROM http_events ORDER BY id DESC LIMIT 50"
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM http_events WHERE event_type = %s
                       ORDER BY id DESC LIMIT 50""",
                    (event_type,),
                ).fetchall()
    except psycopg.Error:
        return {"error": "감시 기록을 조회할 수 없습니다."}, 503

    for row in rows:
        row["occurred_at"] = row["occurred_at"].isoformat()
    return {"events": rows}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5200)
