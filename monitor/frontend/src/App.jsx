import { useState } from "react";

async function requestJson(path, method = "GET", data = null) {
  const options = {
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
  };
  if (data !== null) {
    options.body = JSON.stringify(data);
  }
  const response = await fetch(path, options);
  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.error);
  }
  return result;
}

function LoginForm(props) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  function changeUsername(event) {
    setUsername(event.target.value);
  }

  function changePassword(event) {
    setPassword(event.target.value);
  }

  function handleSubmit(event) {
    event.preventDefault();
    props.onLogin(username, password);
  }

  return (
    <section className="panel">
      <h1>{props.title}</h1>
      <p className="muted">운영자 계정으로 로그인해 주세요.</p>
      <form onSubmit={handleSubmit}>
        <label>아이디<input value={username} onChange={changeUsername} autoComplete="username" /></label>
        <label>비밀번호<input type="password" value={password} onChange={changePassword} autoComplete="current-password" /></label>
        <button className="primary" type="submit" disabled={props.busy}>로그인</button>
      </form>
    </section>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function login(username, password) {
    setBusy(true);
    setError("");
    try {
      const data = await requestJson("/api/auth/login", "POST", { username, password });
      setUser(data.user);
    } catch (error) {
      setError(error.message);
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    setUser(null);
    setError("");
  }

  if (user === null) {
    return (
      <main className="login-shell">
        <LoginForm title="감시 서비스 로그인" onLogin={login} busy={busy} />
        {error && <p className="error" role="alert">{error}</p>}
      </main>
    );
  }
  return (
    <main className="shell">
      <header className="page-header">
        <div><h1>감시 서비스</h1><p>{user.username}님이 로그인했습니다.</p></div>
        <button onClick={logout} disabled={busy}>로그아웃</button>
      </header>
      {error && <p className="error" role="alert">{error}</p>}
      <section className="panel"><h2>대시보드</h2><p>다음 시간에는 관찰 메모와 요청 기록을 불러옵니다.</p></section>
    </main>
  );
}