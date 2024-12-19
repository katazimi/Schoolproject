// 탭을 보여주는 함수 정의
function showTab(tabId) {
    // 모든 탭 콘텐츠에서 'active' 클래스 제거
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // 선택한 탭 콘텐츠에 'active' 클래스 추가
    const selectedContent = document.getElementById(tabId);
    if (selectedContent) {
        selectedContent.classList.add('active');
    }

    // 모든 탭 버튼에서 'active' 클래스 제거
    document.querySelectorAll('.file-tab').forEach(tab => {
        tab.classList.remove('active');
    });

    // 클릭한 탭에 'active' 클래스 추가
    const selectedTab = document.querySelector(`.file-tab[onclick="showTab('${tabId}')"]`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // 기본적으로 탭 1을 활성화 상태로 설정
    showTab('tab1');

    // 탭 버튼을 클릭할 때마다 해당 탭 콘텐츠를 표시
    document.querySelectorAll('.file-tab').forEach(button => {
        button.addEventListener('click', (event) => {
            const tabId = event.target.getAttribute('onclick').match(/showTab\('(.+?)'\)/)[1];
            showTab(tabId);
        });
    });
});


document.addEventListener('DOMContentLoaded', () => {
    checkLoginStatus(); // 로그인 상태 확인

    const playlistElement = document.getElementById('playlist');
    console.log('playlistElement:', playlistElement);

    if (!playlistElement) {
        console.error('재생 목록을 표시할 요소가 존재하지 않습니다.');
        return;
    }

    fetch(`/user_videos`)
        .then(response => {
            if (!response.ok) {
                throw new Error('서버에서 영상 목록을 가져오는 데 실패했습니다.');
            }
            return response.json();
        })
        .then(data => {
            console.log('받아온 데이터:', data);
            playlistElement.innerHTML = '';

            // 한국어 로케일 및 옵션 설정
            const dateOptions = {
                year: 'numeric',   // '2024'
                month: '2-digit',  // '10'
                day: '2-digit',    // '25'
                hour: '2-digit',   // '01'
                minute: '2-digit', // '33'
                second: '2-digit', // '19'
                hour12: true,      // '오전/오후' 표시
                timeZone: 'GMT' // 한국 시간대
            };

            if (data.videos && data.videos.length > 0) {
                data.videos.forEach(video => {
                    const listItem = document.createElement('div');
                    listItem.classList.add('playlist-item');

                    const videoInfo = document.createElement('div');
                    videoInfo.classList.add('video-info');

                    const videoIndex = document.createElement('span');
                    videoIndex.classList.add('video-id');
                    videoIndex.textContent = video.video_id;

                    const videoName = document.createElement('span');
                    videoName.classList.add('video-name');
                    videoName.textContent = video.video_name;

                    // video.video_date를 한국어 로케일로 변환
                    const videoDateObject = new Date(video.video_date);
                    const formattedDate = new Intl.DateTimeFormat('ko-KR', dateOptions).format(videoDateObject);

                    const videoDate = document.createElement('span');
                    videoDate.classList.add('video-date');
                    videoDate.textContent = formattedDate;

                    videoInfo.appendChild(videoIndex);
                    videoInfo.appendChild(videoName);
                    videoInfo.appendChild(videoDate);

                    const videoActions = document.createElement('div');
                    videoActions.classList.add('video-actions');

                    const playButton = document.createElement('button');
                    playButton.classList.add('play-btn');
                    playButton.textContent = '재생';

                    // 여기서 video_id와 video_name을 데이터 속성에 저장
                    playButton.dataset.videoId = video.video_id; // video.video_id가 유효한 값이어야 합니다.
                    playButton.dataset.videoName = video.video_name; // video.video_name이 유효한 값이어야 합니다.

                    console.log('Play Button Data:', playButton.dataset.videoId, playButton.dataset.videoName);

                    const deleteButton = document.createElement('button');
                    deleteButton.classList.add('delete-btn');
                    deleteButton.textContent = '삭제';
                    deleteButton.dataset.id = video.video_id;

                    videoActions.appendChild(playButton);
                    videoActions.appendChild(deleteButton);

                    listItem.appendChild(videoInfo);
                    listItem.appendChild(videoActions);

                    playlistElement.appendChild(listItem);
                });
            } else {
                playlistElement.innerHTML = '<div>재생할 영상이 없습니다.</div>';
            }
            // 이벤트 위임을 사용해 재생 및 삭제 버튼 클릭 처리
            playlistElement.addEventListener('click', (event) => {
                const playButton = event.target.closest('.play-btn');
                console.log('Closest play button:', playButton);
            
                if (playButton) {
                    const videoId = playButton.getAttribute('data-video-id');
                    const videoName = playButton.getAttribute('data-video-name');
            
                    console.log('Video ID:', videoId);
                    console.log('Video Name:', videoName);
            
                    // 1. 동영상 URL 조합 라우터에 POST 요청 보내기
                    fetch('/get_video_url', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ video_id: videoId, video_name: videoName })
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('받아온 동영상 URL:', data.video_original_r_url);
            
                        // 비디오 URL 목록 만들기 (여기서는 예시로 L/R 동영상을 모두 변환한다고 가정)
                        const videoPaths = [
                            data.video_original_r_url,
                            data.video_original_l_url,
                            data.video_result_r_url,
                            data.video_result_l_url,
                            data.video_r_l_x,
                            data.video_r_l_y,
                            data.video_r_r_x,
                            data.video_r_r_y
                        ];
            
                        // 모든 동영상 변환 요청을 비동기로 처리
                        const conversionPromises = videoPaths.map((videoPath) => {
                            console.log('Converting video:', videoPath);
                            return fetch('/convert_video', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({ video_path: videoPath })
                            }).then(response => response.json());
                        });
            
                        // 모든 변환 요청이 완료될 때까지 기다림
                        return Promise.all(conversionPromises);
                    })
                    .then(results => {
                        // 변환된 동영상 URL들을 가져옴
                        const convertedVideos = results.map(result => result.converted_video_path);
                        console.log('Converted video paths:', convertedVideos);
            
                        // 각 변환된 동영상을 재생 (예시: L, R 각각 재생)
                        playVideo(convertedVideos[0], 'tab1-right-video');
                        playVideo(convertedVideos[1], 'tab1-left-video')
                        playVideo(convertedVideos[2], 'tab2-right-video')
                        playVideo(convertedVideos[3], 'tab2-left-video')
                        playVideo(convertedVideos[4], 'tab3-right1-video')
                        playVideo(convertedVideos[5], 'tab3-left1-video')
                        playVideo(convertedVideos[6], 'tab3-right2-video')
                        playVideo(convertedVideos[7], 'tab3-left2-video');
                    })
                    .catch(error => {
                        console.error('동영상 URL을 가져오는 중 오류 발생 또는 변환 실패:', error);
                    });
                }
            
                if (event.target.classList.contains('delete-btn')) {
                    const videoId = event.target.getAttribute('data-id');
                    console.log('삭제할 Video ID:', videoId);
                    deleteVideo(videoId);
                }
            });
            
        })
        .catch(error => {
            console.error('영상 데이터를 불러오는 중 오류 발생:', error);
        });

    // 로그아웃 버튼 클릭 처리
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            window.location.href = '/logout'; // 로그아웃 라우트로 이동
        });
    }
});

function playVideo(videoSrc) {
    const leftVideo = document.getElementById('tab1-left-video');
    // const rightVideo = document.getElementById('right-video');

    if (!leftVideo) {
        console.error('left-video 요소를 찾을 수 없습니다.');
        return;
    }

    // 비디오 요소의 src 설정
    leftVideo.src = videoSrc;
    // rightVideo.src = videoSrc;

    // 비디오 재생
    leftVideo.play();
    // rightVideo.play();
}

function playVideo(videoSrc, videoElementId) {
    const videoElement = document.getElementById(videoElementId);
    if (videoElement) {
        videoElement.src = videoSrc;
        videoElement.play();
    } else {
        console.error(`비디오 요소를 찾을 수 없습니다: ${videoElementId}`);
    }
}


// 로그인 상태를 설정하는 함수
function setLoginStatus(status) {
    isLoggedIn = status;
    if (!isLoggedIn) {
        showAlert('로그인 후 이용해 주세요');
        console.log(isLoggedIn);
        setTimeout(() => {
            window.location.href = '/login'; // 로그인 페이지의 URL로 이동
        }, 1500); // 10000 밀리초 = 10초
    }
}

// 로그인 상태를 가져와 설정하는 함수
function checkLoginStatus() {
    const loggedInStatus = document.getElementById('loggedInStatus-info').innerText;
    setLoginStatus(loggedInStatus === 'True'); // 'True'일 경우 로그인 상태 설정
}