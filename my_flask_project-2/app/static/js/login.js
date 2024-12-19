form.addEventListener('submit', (event) => {
    const email = form.email.value.trim();
    const password = form.password.value.trim();

    if (!email || !password) {
        event.preventDefault();
        messageDiv.textContent = '이메일과 비밀번호를 모두 입력해주세요.';
        return;
    }

    // 실제 서버로 로그인 요청 보내기
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            email: email,
            password: password
        })
    })
    .then(response => {
        if (response.ok) {
            // 로그인 성공 시
            handleLogin();
        } else {
            // 로그인 실패 시 메시지 표시
            messageDiv.textContent = '이메일 또는 비밀번호가 올바르지 않습니다.';
        }
    })
    .catch(error => {
        console.error('로그인 요청 중 오류 발생:', error);
        messageDiv.textContent = '로그인 중 오류가 발생했습니다. 나중에 다시 시도해 주세요.';
    });

    // 기본 동작 방지: 서버 응답을 확인할 때까지 폼 제출 방지
    event.preventDefault();
});
