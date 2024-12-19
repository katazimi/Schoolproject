// 모달 요소를 가져옵니다.
const alertModal = document.querySelector('.alert-modal');
const alertContent = document.querySelector('.alert-content');
const alertBtn = document.querySelector('.alert-btn');

// 알림 메시지를 표시하는 함수
function showAlert(message) {
    const alertModal = document.querySelector('.alert-modal');
    const alertMessage = document.getElementById('alert-message');
    
    // 메시지를 설정할 때 innerHTML을 사용하여 HTML 태그를 해석하도록 합니다.
    alertMessage.innerHTML = message;
    
    alertModal.style.display = 'flex';

    const alertBtn = document.querySelector('.alert-btn');
    alertBtn.addEventListener('click', () => {
        alertModal.style.display = 'none';
    });
}


// 모달을 숨기는 함수
function hideAlert() {
    alertModal.style.display = 'none';
}

// 모달 외부를 클릭했을 때 모달 닫기
alertModal.addEventListener('click', (event) => {
    if (event.target === alertModal) {
        hideAlert();
    }
});

// 모달의 확인 버튼을 클릭했을 때 모달 닫기
alertBtn.addEventListener('click', hideAlert);
