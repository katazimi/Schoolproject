// 비디오 플레이어와 관련된 요소들을 가져옵니다.
const videoPlayer = document.getElementById('video-player');
const playlist = document.getElementById('playlist');
const currentVideoLabel = document.getElementById('current-video');
const playButton = document.querySelector('.control-btn.play');
const pauseButton = document.querySelector('.control-btn.pause');
const stopButton = document.querySelector('.control-btn.stop');
const volumeButton = document.querySelector('.control-btn.volume');
const volumeValue = document.querySelector('.volume-value');
const volumeSlider = document.querySelector('.volume-slider');
const settingsButton = document.querySelector('.control-btn.settings');
const settingsMenu = document.querySelector('.settings-menu');
const playbackRateSelect = document.getElementById('playback-rate');
const autoplayCheckbox = document.getElementById('autoplay');
const loopCheckbox = document.getElementById('loop');
const subtitleInput = document.getElementById('subtitle-input');
const fullscreenButton = document.getElementById('fullscreen-button');
const controlToggle = document.getElementById('control-toggle'); 
const controlsContainer = document.querySelector('.video-controls');
const progressBar = document.querySelector('.progress-bar');
const analysisButton = document.getElementById('start-analysis-button');
const timeDisplay = document.querySelector('.time-display'); // 예: "0:00 / 0:00"

// 재생 목록과 URL을 저장할 배열
let videoFiles = [];
let videoURLs = [];
let isAnalysisRunning = false;
let selectedFile = null;
let userId = document.getElementById('user-info').innerText;

// // 파일 선택 시 재생 목록에 추가
// document.getElementById('file-input').addEventListener('change', (event) => {
//     addFiles(event.target.files);
//     selectedFile = event.target.files;
// });

const fileInput = document.getElementById('file-input');
if (fileInput) {
    fileInput.addEventListener('change', (event) => {
        addFiles(event.target.files);
        selectedFile = event.target.files[0];
        console.log('File selected:', selectedFile.name);
    });
} else {
    console.error('File input element not found');
}



/// 선택한 파일을 재생 목록에 추가하는 함수
function addFiles(files) {
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        videoFiles.push(file);

        // 재생 목록 항목 생성
        const listItem = document.createElement('div');
        listItem.classList.add('playlist-item');

        // 동영상 정보 표시 (파일 이름 및 재생 시간)
        const videoInfo = document.createElement('div');
        videoInfo.classList.add('video-info');
        const videoDuration = document.createElement('span');
        videoDuration.classList.add('video-duration');
        videoDuration.textContent = '--:--'; // 초기 값 설정

        videoInfo.innerHTML = `<p>${file.name}</p>`;
        videoInfo.appendChild(videoDuration);

        // 재생 버튼 추가
        const playButton = document.createElement('button');
        playButton.classList.add('play-button');
        playButton.textContent = '재생';
        playButton.addEventListener('click', () => playVideo(file));

        // 삭제 버튼 추가
        const deleteButton = document.createElement('button');
        deleteButton.classList.add('delete-button');
        deleteButton.textContent = '삭제';
        deleteButton.addEventListener('click', () => removeFromPlaylist(file, listItem));

        listItem.appendChild(videoInfo);
        listItem.appendChild(playButton);
        listItem.appendChild(deleteButton);

        // 재생 목록에 항목 추가
        const playlistItems = document.querySelector('.playlist-items');
        playlistItems.appendChild(listItem);

        // 동영상 시간을 가져오기 위해 URL을 생성하고, 메타데이터를 로드
        const tempVideo = document.createElement('video');
        tempVideo.src = URL.createObjectURL(file);
        tempVideo.addEventListener('loadedmetadata', () => {
            const duration = tempVideo.duration;
            const formattedDuration = formatTime(duration);
            videoDuration.textContent = formattedDuration;
            URL.revokeObjectURL(tempVideo.src); // URL 해제
        });
    }
}


// 재생 목록에서 항목을 제거하는 함수
function removeFromPlaylist(file, listItem) {
    const index = videoFiles.indexOf(file);
    if (index > -1) {
        videoFiles.splice(index, 1); // 배열에서 파일 제거
        listItem.remove(); // 화면에서 항목 제거

        // 현재 재생 중인 파일을 제거하는 경우 비디오 플레이어 초기화
        if (currentVideoLabel.textContent === file.name) {
            videoPlayer.pause(); // 재생 중지
            videoPlayer.src = ''; // 비디오 소스 초기화
            currentVideoLabel.textContent = '선택되지 않음'; // 현재 재생 중인 파일 라벨 업데이트
            videoPlayer.load(); // 비디오 로드 초기화
        }
    }
}

// 선택한 비디오 파일을 재생하는 함수
function playVideo(file) {
    if (videoURLs.length > 0) {
        URL.revokeObjectURL(videoPlayer.src);
    }

    const videoURL = URL.createObjectURL(file);
    videoPlayer.src = videoURL;
    videoPlayer.play();
    currentVideoLabel.textContent = file.name;
    videoURLs.push(videoURL);
}

// 재생 목록 초기화 함수
function clearPlaylist() {
    // 비디오 파일 및 URL 배열 초기화
    videoFiles = [];
    videoURLs.forEach(url => URL.revokeObjectURL(url)); // 기존에 생성된 URL 해제
    videoURLs = [];

    // 재생 목록 화면에서 항목 지우기
    const playlistItems = document.querySelector('.playlist-items');
    if (playlistItems) {
        playlistItems.innerHTML = '';
    }

    // 비디오 플레이어 초기화
    videoPlayer.pause(); // 비디오 재생 중지
    videoPlayer.src = '';
    currentVideoLabel.textContent = '선택되지 않음';
    videoPlayer.load(); // 비디오 재로딩을 강제하여 초기화 상태로 유지
}

// 초기 상태 설정: 일시정지 버튼 숨기기
pauseButton.style.display = 'none';

// 재생바 업데이트
videoPlayer.addEventListener('timeupdate', updateDisplayTime);
videoPlayer.addEventListener('loadedmetadata', updateDisplayTime);

// 시간 업데이트 함수
function updateDisplayTime() {
    const currentTime = formatTime(videoPlayer.currentTime);
    const duration = formatTime(videoPlayer.duration);
    timeDisplay.textContent = `${currentTime} / ${duration}`;
    progressBar.value = (videoPlayer.currentTime / videoPlayer.duration) * 100;
}

// 시간을 분:초 형식으로 변환하는 함수
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
}

// 재생바 클릭 시 비디오 위치 변경
progressBar.addEventListener('input', () => {
    const newTime = (progressBar.value / 100) * videoPlayer.duration;
    videoPlayer.currentTime = newTime;
});

// 초기 상태 설정: 일시정지 버튼 숨기기
pauseButton.style.display = 'none';

// 재생 및 일시정지 버튼 제어
playButton.addEventListener('click', () => {
    videoPlayer.play();
    updatePlayPauseButton();
});
pauseButton.addEventListener('click', () => {
    videoPlayer.pause();
    updatePlayPauseButton();
});

// 재생 상태에 따라 버튼 업데이트
function updatePlayPauseButton() {
    if (videoPlayer.paused || videoPlayer.ended) {
        playButton.style.display = 'block'; // 재생 버튼 보이기
        pauseButton.style.display = 'none'; // 일시정지 버튼 숨기기
    } else {
        playButton.style.display = 'none'; // 재생 버튼 숨기기
        pauseButton.style.display = 'block'; // 일시정지 버튼 보이기
    }
}

// 비디오가 재생되거나 일시정지될 때마다 버튼 상태를 업데이트
videoPlayer.addEventListener('play', updatePlayPauseButton);
videoPlayer.addEventListener('pause', updatePlayPauseButton);
videoPlayer.addEventListener('ended', updatePlayPauseButton);

// 정지 버튼 클릭 시 비디오 정지 및 처음으로 되돌림
stopButton.addEventListener('click', () => {
    videoPlayer.pause();
    videoPlayer.currentTime = 0;
    updatePlayPauseButton();
});


// 볼륨 슬라이더 초기 상태: 숨김
let isSliderVisible = false;
volumeSlider.style.display = 'none';
volumeValue.style.display = 'none';

// 볼륨 버튼 클릭 시 - 슬라이더와 볼륨 값 표시/숨기기 토글
volumeButton.addEventListener('click', () => {
    isSliderVisible = !isSliderVisible;
    volumeSlider.style.display = isSliderVisible ? 'inline-block' : 'none';
    volumeValue.style.display = isSliderVisible ? 'inline-block' : 'none';
});

// 볼륨 슬라이더 변경 시 - 볼륨 조절 및 볼륨 값 업데이트
volumeSlider.addEventListener('input', (event) => {
    const volume = event.target.value;
    videoPlayer.volume = volume; // 볼륨 조절 (0~1)
    const volumePercent = Math.floor(volume * 100); // 퍼센트로 변환
    volumeValue.textContent = `${volumePercent}`; // 볼륨 값 표시

    // 볼륨 값에 따른 아이콘 변경
    if (volumePercent == 0) {
        volumeButton.innerHTML = '<i class="fas fa-volume-mute"></i>';
    } else if (volumePercent <= 50) {
        volumeButton.innerHTML = '<i class="fas fa-volume-down"></i>';
    } else {
        volumeButton.innerHTML = '<i class="fas fa-volume-up"></i>';
    }
});

// 컨트롤 관련 변수 및 함수
let controlsLocked = false; // 컨트롤 고정 여부
let hideControlsTimeout;

// 컨트롤 표시 함수
function showControls() {
    controlsContainer.style.opacity = '1'; // 컨트롤 표시
    if (!controlsLocked) {
        clearTimeout(hideControlsTimeout);
        hideControlsTimeout = setTimeout(hideControls, 5000); // 5초 후 컨트롤 숨기기
    }
}

// 컨트롤 숨김 함수
function hideControls() {
    if (!controlsLocked) {
        controlsContainer.style.opacity = '0'; // 컨트롤 숨기기
    }
}

// 컨트롤 고정 여부 변경 시 - 고정 시 컨트롤 숨기기 타이머 해제
controlToggle.addEventListener('change', () => {
    controlsLocked = controlToggle.checked;
    if (controlsLocked) {
        clearTimeout(hideControlsTimeout);
        showControls(); // 고정 시 컨트롤 표시
    }
});

// 비디오 플레이어 및 컨트롤에 마우스를 올릴 때 컨트롤 표시
videoPlayer.addEventListener('mousemove', showControls);
controlsContainer.addEventListener('mousemove', showControls);

let isMenuVisible = false;

// 설정 버튼 클릭 시 - 설정 메뉴 보이기/숨기기 
settingsButton.addEventListener('click', () => {
    if (settingsMenu.style.display === 'none' || settingsMenu.style.opacity === '0') {
        settingsMenu.style.display = 'block';
        settingsMenu.classList.add('show');
    } else {
        settingsMenu.classList.remove('show');
        setTimeout(() => {
            settingsMenu.style.display = 'none';
        }, 300); // 애니메이션 시간 이후에 display를 none으로 설정
    }
});

// 설정 메뉴를 설정 버튼 위에 위치시키는 함수
function positionSettingsMenu() {
    const buttonRect = settingsButton.getBoundingClientRect();
    const menuRect = settingsMenu.getBoundingClientRect();
    const offsetTop = buttonRect.top - menuRect.height - 10; // 버튼 위로 10px 여유 공간 추가
    const offsetLeft = buttonRect.left - (menuRect.width / 2) + (buttonRect.width / 2);

    settingsMenu.style.top = `${offsetTop}px`;
    settingsMenu.style.left = `${offsetLeft}px`;
}

// 재생 속도 변경
playbackRateSelect.addEventListener('change', (event) => {
    videoPlayer.playbackRate = parseFloat(event.target.value); // 선택한 재생 속도 설정
});

// 자동 재생 설정
autoplayCheckbox.addEventListener('change', (event) => {
    videoPlayer.autoplay = event.target.checked; // 체크 여부에 따라 자동 재생 설정
});

// 루프 설정
loopCheckbox.addEventListener('change', (event) => {
    videoPlayer.loop = event.target.checked; // 체크 여부에 따라 루프 설정
});


// 전체 화면 버튼 클릭 시 - 전체 화면 모드로 전환
fullscreenButton.addEventListener('click', () => {
    if (videoPlayer.requestFullscreen) {
        videoPlayer.requestFullscreen();
    } else if (videoPlayer.webkitRequestFullscreen) {
        videoPlayer.webkitRequestFullscreen();
    } else if (videoPlayer.mozRequestFullScreen) {
        videoPlayer.mozRequestFullScreen();
    } else if (videoPlayer.msRequestFullscreen) {
        videoPlayer.msRequestFullscreen();
    }
});


if (analysisButton) {
    analysisButton.addEventListener('click', () => {
        console.log('Analysis button clicked');
        console.log(userId)
        if (!selectedFile) {
            console.error('No file selected');
            showAlert('Please select a file first.');
            return;
        }

        if (isAnalysisRunning) {
            console.log('Analysis is already running');
            return; // 이미 실행 중이라면 중복 실행 방지
        }
        isAnalysisRunning = true;
        console.log('Starting file upload');

        // 파일 업로드 시작
        const formData = new FormData();
        formData.append('videoFile', selectedFile, selectedFile.name);
        formData.append('user_id', userId);  // userId를 추가하여 서버로 전송

        fetch('/upload-video', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Video uploaded successfully:', data.filePath);
                showAlert('비디오 업로드가 완료 되었습니다. <br> 분석이 시작됩니다...');
                startAnalysis();
            } else {
                console.error('Failed to upload video:', data.message);
                showAlert('Failed to upload video: ' + data.message);
                isAnalysisRunning = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error uploading video: ' + error.message);
            isAnalysisRunning = false;
        });
    });
} else {
    console.error('Analysis button element not found');
}


// 이석증 판별 시작 함수
function startAnalysis() {
    const progressBarContainer = document.querySelector('.progress-bar-container');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    progressBarContainer.style.display = 'block';
    progressBar.value = 0;
    progressText.textContent = '0%';

    // 알고리즘 실행 요청
    fetch('/run-analysis', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 분석이 시작되면 진행률 업데이트 시작
            updateProgress();
        } else {
            showAlert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('서버 오류로 인해 분석을 시작할 수 없습니다.');
    });
}



function updateProgress() {
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    const interval = setInterval(() => {
        fetch('/progress')
            .then(response => response.json())
            .then(data => {
                progressBar.value = data.progress;
                progressText.textContent = `${data.progress}%`;

                if (data.progress >= 100) {
                    clearInterval(interval);
                    progressText.textContent = '분석 완료';
                    showAlert('이석증 판별이 완료되었습니다. 결과를 확인해주세요.');
                    setTimeout(() => {
                        document.querySelector('.progress-bar-container').style.display = 'none';
                    }, 2000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('진행 상태를 가져오는 중 오류가 발생했습니다.');
                clearInterval(interval);
            });
    }, 1000);  // 1초마다 진행 상태 업데이트
}

// 이석증 판별 버튼의 상태를 업데이트하는 함수
function updateAnalysisButton() {
    const analysisButton = document.getElementById('start-analysis-button');
    if (isLoggedIn) {
        analysisButton.disabled = false;
        analysisButton.classList.remove('disabled');
    } else {
        analysisButton.disabled = true;
        analysisButton.classList.add('disabled');
    }
}
// 로그인 상태를 설정하는 함수
function setLoginStatus(status) {
    isLoggedIn = status;
    updateAnalysisButton();
}

// 초기 설정: 로그아웃 상태로 설정
setLoginStatus(false);

// 로그인 상태를 가져와 설정하는 함수
function checkLoginStatus() {
    const loggedInStatus = document.getElementById('loggedInStatus-info').innerText;
    console.log(loggedInStatus)
    setLoginStatus(loggedInStatus === 'True'); // 'true'일 경우 로그인 상태 설정
}

// 페이지 로드 시 로그인 상태 확인
document.addEventListener('DOMContentLoaded', () => {
    checkLoginStatus(); // 로그인 상태 확인
});

