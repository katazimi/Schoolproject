document.addEventListener('DOMContentLoaded', function() {
    const passwordForm = document.getElementById('password-form');
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const errorMessage = document.getElementById('error-message');

    passwordForm.addEventListener('submit', function(event) {
        const newPassword = newPasswordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        // 새 비밀번호와 비밀번호 확인이 일치하지 않을 경우
        if (newPassword !== confirmPassword) {
            errorMessage.textContent = '새 비밀번호와 비밀번호 확인이 일치하지 않습니다.';
            event.preventDefault(); // 폼 제출 막기
        } else {
            errorMessage.textContent = ''; // 오류 메시지 지우기
        }
    });
});


// 로그인 상태를 설정하는 함수
function setLoginStatus(status) {
    isLoggedIn = status;
    console.log(isLoggedIn)
    if (!isLoggedIn) {
        window.location.href = '/login'; // 로그인 페이지의 URL로 이동
    }
}

// 로그인 상태를 가져와 설정하는 함수
function checkLoginStatus() {
    const loggedInStatus = document.getElementById('loggedInStatus-info').innerText;
    setLoginStatus(loggedInStatus === 'True'); // 'true'일 경우 로그인 상태 설정
}

// 페이지 로드 시 로그인 상태 확인
document.addEventListener('DOMContentLoaded', () => {
    checkLoginStatus(); // 로그인 상태 확인
});

document.getElementById('logout-button').addEventListener('click', () => {
    // 로그아웃 라우트를 호출하여 로그아웃 처리
    window.location.href = '/logout'; // Flask의 /logout 경로로 이동
});
