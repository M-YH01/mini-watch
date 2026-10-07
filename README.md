# Mini Watch

일반 서비스(게시판)와 감시 서비스(React 대시보드 + Flask API)로 이루어진 실습 프로젝트입니다.

| 서비스 | 위치 | 주소 |
| --- | --- | --- |
| 일반 서비스 (Flask, 게시판) | `general/` | http://127.0.0.1:5100 |
| 감시 API (Flask) | `monitor/backend/` | http://127.0.0.1:5200 |
| 감시 화면 (React + Vite) | `monitor/frontend/` | http://127.0.0.1:5173 |

React의 `/api` 요청은 Vite 프록시가 감시 Flask(5200)로 전달합니다. 프론트엔드는 DB에 직접 접속하지 않습니다.

## 사용한 시작 자료와 직접 구현한 부분

- 수업 시작 자료: https://github.com/zeroskill2400/mini-watch (day03-start, day04-start). DB 준비 SQL, `.env.example` 형식, Vite 프로젝트 틀을 사용했습니다.
- 직접 구현·수정: 일반 서비스 게시판 CRUD와 모듈 분리, 요청 기록 전송, 감시 API의 로그인·요청 기록·메모 CRUD, React 컴포넌트·API 모듈 구성, 입력 검증(400)과 없는 자료 처리(404).

## 필수 기능 구현 현황

- 로그인: React state의 입력값을 `POST /api/auth/login`으로 전송합니다. Flask가 DB의 `password_hash`를 `check_password_hash`로 검증합니다. 빈 입력은 400, 계정 불일치는 401을 반환하고 화면에 오류 안내를 표시합니다.
- 대시보드: 로그인 성공 시 사용자 이름을 표시하고, 로그아웃하면 로그인 폼으로 돌아갑니다.
- 요청 기록: `GET /api/events`의 메서드·경로·상태 코드를 표로 표시합니다. 비어 있을 때와 조회에 실패했을 때 안내를 표시합니다.
- 관찰 메모: 목록(`GET /api/notes`), 상세(`GET /api/notes/<번호>`), 작성(`POST`), 수정(`PUT`), 삭제(`DELETE`)를 구현했습니다. 삭제는 확인 화면을 거치고 취소하면 보존합니다. 저장·수정·삭제 후 목록을 다시 조회합니다.
- `목록 새로고침` 버튼으로 메모와 요청 기록을 다시 조회합니다.
- 제목·내용의 앞뒤 공백을 제거한 뒤 비어 있으면 400을 반환하고 DB를 변경하지 않습니다. 없는 번호의 조회·수정·삭제는 404를 반환합니다.
- 모든 SQL은 `%s` 매개변수로 값을 전달하며 `psycopg`와 `connect_db()`를 사용합니다.

심화 과제는 구현하지 않았습니다.

## 폴더 구조

```
general/                    # 일반 서비스
├─ app.py                   # 앱 생성·라우터 등록·실행
├─ routes/                  # HTTP 요청·응답
├─ repositories/            # SQL 실행
├─ db.py                    # DB 연결
├─ request_logging.py       # 요청 기록을 감시 서비스로 전송
├─ templates/, static/
└─ sql/
monitor/
├─ backend/
│  ├─ app.py
│  ├─ routes/               # auth.py, events.py, notes.py
│  ├─ repositories/         # users.py, events.py, notes.py
│  ├─ note_rules.py         # 메모 입력 검증
│  ├─ db.py
│  └─ sql/
└─ frontend/
   └─ src/
      ├─ App.jsx            # 로그인 전후 화면 연결
      ├─ components/        # LoginForm, Dashboard, NoteList, NoteDetail, NoteForm, DeleteConfirm, EventList
      └─ api/               # client.js, auth.js, events.js, notes.js
```

## 실행 방법 (Windows CMD)

준비물: Python 3, Node.js, PostgreSQL, pgAdmin

### 1. DB 준비

pgAdmin의 Query Tool에서 순서대로 실행합니다.

1. `monitor/backend/sql/create_database.sql`을 실행해 `general_db`, `monitor_db`를 만듭니다. 이미 있으면 건너뜁니다.
2. `general_db`의 Query Tool에서 `general/sql/day04.sql` 전체를 실행합니다.
3. `monitor_db`의 Query Tool에서 `monitor/backend/sql/day04.sql` 전체를 실행합니다.

### 2. 환경 설정

`general`과 `monitor\backend` 폴더에서 `.env.example`을 복사해 `.env`를 만듭니다.

```
copy .env.example .env
```

| 설정 | 용도 |
| --- | --- |
| `DB_HOST`, `DB_PORT` | PostgreSQL 주소 (기본 127.0.0.1, 5432) |
| `DB_NAME` | 서비스별 DB 이름 (`general_db`, `monitor_db`) |
| `DB_USER`, `DB_PASSWORD` | PostgreSQL 계정. 비밀번호는 본인 값으로 바꿉니다. |
| `SECRET_KEY` | 세션 서명용 비밀 값. 아래 명령 결과를 붙여 넣습니다. |

```
py -c "import secrets; print(secrets.token_urlsafe(48))"
```

`.env`는 Git에 올리지 않습니다.

### 3. 일반 서비스 실행 (CMD 창 1)

```
cd general
py -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python create_user.py
python app.py
```

### 4. 감시 API 실행 (CMD 창 2)

```
cd monitor\backend
py -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python create_user.py
python app.py
```

### 5. 감시 화면 실행 (CMD 창 3)

```
cd monitor\frontend
npm install
npm run dev
```

브라우저에서 http://127.0.0.1:5173 을 엽니다.

## 테스트 계정

`create_user.py`가 만드는 수업용 예시 계정입니다.

| 서비스 | 아이디 | 비밀번호 |
| --- | --- | --- |
| 감시 화면 | `operator` | `Learn123!` |
| 일반 서비스 | `student` | `Learn123!` |

## 통합 확인 결과

1. 일반 게시판에서 게시글과 없는 주소(404)에 접속해 요청 기록이 생기는 것을 확인했습니다.
2. 감시 화면에서 틀린 비밀번호로 오류 안내를 확인하고 올바른 계정으로 로그인했습니다.
3. 요청 기록의 경로와 상태 코드가 접속한 내용과 일치합니다.
4. 메모를 작성·수정하고, 공백뿐인 내용은 400 오류 안내와 함께 기존 내용이 유지됩니다.
5. 삭제 취소와 삭제 확정이 각각 동작합니다.
6. 새로고침 후 다시 로그인해도 메모가 유지되고, 로그아웃하면 로그인 폼으로 돌아옵니다.
