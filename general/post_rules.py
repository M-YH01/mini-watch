def clean_title_body(form):
    title = (form.get("title") or "").strip()
    body = (form.get("body") or "").strip()
    return title, body


def validate_post(title, body):
    if not title or not body:
        return "제목과 내용을 모두 입력해 주세요."
    return None
