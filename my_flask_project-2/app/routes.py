from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User, Video, db 
from datetime import datetime
import os
import cv2
import getpass

main = Blueprint('main', __name__)

@main.route('/')
def home():
    # 로그인 여부에 따라 loggedInStatus 설정
    loggedInStatus = 'user_id' in session
    user = None

    if loggedInStatus:
        user = User.query.get(session['user_id'])
    
    print(loggedInStatus, user)
    
    return render_template('Home.html', loggedInStatus=loggedInStatus, user=user)

# 로그인 라우트
@main.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id  # 세션에 사용자 ID 저장
            flash('로그인에 성공했습니다!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('이메일 또는 비밀번호가 올바르지 않습니다.', 'danger')

    return render_template('login.html')


# 로그아웃 라우트
@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('main.home'))

# 프로필 페이지 라우트
@main.route('/profile')
def profile():
    #로그인 여부에 따라 loggedInStatus 설정
    loggedInStatus = 'user_id' in session
    user = None

    if loggedInStatus:
        user = User.query.get(session['user_id'])
    print(user, loggedInStatus)

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # 현재 비밀번호 확인
        if not check_password_hash(user.password, current_password):
            flash('현재 비밀번호가 올바르지 않습니다.', 'danger')
            return redirect(url_for('main.profile'))
        
        # 새 비밀번호와 확인용 비밀번호가 일치하는지 확인
        if new_password != confirm_password:
            flash('새 비밀번호와 비밀번호 확인이 일치하지 않습니다.', 'danger')
            return redirect(url_for('main.profile'))
        
        # 새 비밀번호를 해시 처리 후 저장
        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('비밀번호가 성공적으로 변경되었습니다.', 'success')
        return redirect(url_for('main.profile'))

    return render_template('profile.html', loggedInStatus=loggedInStatus, user=user)


@main.route('/results')
def results():
    # 로그인 여부에 따라 loggedInStatus 설정
    loggedInStatus = 'user_id' in session
    user = None

    if loggedInStatus:
        user = User.query.get(session['user_id'])
    
    print(loggedInStatus, user)
    
    return render_template('results.html', loggedInStatus=loggedInStatus, user=user)


# 회원가입 라우트 추가
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('이미 등록된 이메일입니다.', 'danger')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)  # 비밀번호 암호화 저장
            db.session.add(new_user)
            db.session.commit()
            flash('회원가입에 성공했습니다! 이제 로그인하세요.', 'success')
            return redirect(url_for('main.login'))

    return render_template('register.html')


# 비디오 업로드를 처리하는 upload_bp Blueprint
upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload-video', methods=['POST'])
def upload_video():
    try:
        print("Request received for video upload.")
        if 'videoFile' not in request.files:
            print("No file part in the request.")
            return jsonify(success=False, message='No file part'), 400

        file = request.files['videoFile']
        user_id = request.form.get('user_id')
        if file.filename == '':
            print("No file selected.")
            return jsonify(success=False, message='No selected file'), 400

        # UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../videos')
        path = os.path.dirname(__file__)
        updated_path = path.replace("\\app", "")
        UPLOAD_FOLDER = os.path.join(updated_path,'videos')
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        # 안전한 파일 이름 설정
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        print(f"Secure filename set: {filename}")

        date = datetime.now().strftime("%y%m%d%H%M")

        new_name = date + "_" + user_id + "_" + filename

        # 파일을 서버에 저장
        save_path = os.path.join(UPLOAD_FOLDER, new_name)
        print(f"Saving file to: {save_path}")
        try:
            with open(save_path, 'wb') as f:
                # 파일 내용을 청크 단위로 읽어서 저장
                for chunk in file.stream:
                    f.write(chunk)
            print("File saved successfully.")
        except OSError as e:
            print(f"Failed to save file: {str(e)}")
            return jsonify(success=False, message=f"Failed to save file: {str(e)}"), 500


        # 비디오 메타데이터 추출
        try:
            print("Extracting video metadata.")
            metadata = extract_video_metadata(save_path)
            video_length = metadata['length']
            video_fps = metadata['fps']
            video_width = metadata['width']
            video_height = metadata['height']
            print(f"Metadata extracted: length={video_length}, fps={video_fps}, width={video_width}, height={video_height}")
        except ValueError as e:
            print(f"Metadata extraction error: {str(e)}")
            return jsonify(success=False, message=f"Metadata extraction error: {str(e)}"), 500

        # 비디오 관련 정보 설정
        video_name = filename
        try:
            video_size = os.path.getsize(save_path)  # 파일 크기 (바이트)
            print(f"File size: {video_size} bytes")
        except OSError as e:
            print(f"Failed to get file size: {str(e)}")
            return jsonify(success=False, message=f"Failed to get file size: {str(e)}"), 500

        video_date = datetime.now()

        # 가장 최근의 비디오 ID를 가져와서 숫자 부분 추출
        try:
            print("Querying the latest video ID.")
            latest_video = Video.query.order_by(Video.id.desc()).first()
            new_number = latest_video.id + 1 if latest_video else 1
            print(f"New video ID: {new_number}")
        except Exception as e:
            print(f"Database query error: {str(e)}")
            return jsonify(success=False, message=f"Database query error: {str(e)}"), 500

        # 비디오 정보 데이터베이스에 저장
        new_video = Video(
            id=new_number,
            user_id = user_id,
            name=video_name,
            file_path=save_path,
            length=video_length,
            fps=video_fps,
            width=video_width,
            height=video_height,
            date=video_date,
            size=video_size
        )
        try:
            print("Saving video information to the database.")
            db.session.add(new_video)
            db.session.commit()
            print("Video information saved to the database successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Database commit error: {str(e)}")
            return jsonify(success=False, message=f"Database commit error: {str(e)}"), 500

        print(f"File saved as: {save_path}")
        print(f"Extracted file name: {video_name}")

        return jsonify(success=True, filePath=save_path, videoName=video_name, videoId=new_number)
    except Exception as e:
        print(f"Unexpected server error: {str(e)}")
        return jsonify(success=False, message=f"Unexpected server error: {str(e)}"), 500

def extract_video_metadata(video_path):
    """OpenCV를 사용해 비디오 파일의 길이, FPS, 해상도를 추출합니다."""
    video_capture = cv2.VideoCapture(video_path)

    if not video_capture.isOpened():
        raise ValueError("Could not open the video file.")

    # 프레임 수와 FPS를 사용해 비디오 길이 계산
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    video_length = frame_count / fps if fps > 0 else 0

    # 해상도 추출
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))


    return {
        'length': round(video_length, 2),  # 비디오 길이를 소수점 2자리까지 반올림
        'fps': round(fps, 2),  # FPS를 소수점 2자리까지 반올림
        'width': width,
        'height': height
    }


import threading
from .utils.nd_algorithm import ND
from flask import current_app

# 전역 변수로 진행률 상태 저장
progress_status = {"progress": 0}

def progress_callback(progress):
    global progress_status
    progress_status["progress"] = progress

@upload_bp.route('/run-analysis', methods=['POST'])
def run_analysis():
    try:
        # user_id와 video_id를 POST 요청에서 받습니다.
        user_id = request.json.get('user_id')
        
        if not user_id: 
            return jsonify(success=False, message="Missing user_id"), 400

        # ND 알고리즘을 비동기적으로 실행
        def run_nd_algorithm(app, user_id):
            try:
                with app.app_context():  # 애플리케이션 컨텍스트 설정
                    print("ND 알고리즘 시작")
                    nd_instance = ND()
                    print("ND 인스턴스 생성 완료")
                    nd_instance.System(user_id=user_id, progress_callback=progress_callback)
                    print("ND System 메서드 실행 완료")
            except Exception as e:
                print(f"Error running ND algorithm: {e}")
        
        # 현재 애플리케이션 객체를 가져옵니다.
        app = current_app._get_current_object()

        # 별도의 스레드에서 ND 알고리즘 실행
        thread = threading.Thread(target=run_nd_algorithm, args=(app, user_id))
        thread.start()

        # 알고리즘 실행이 시작됨을 클라이언트에 반환
        return jsonify(success=True, message="Algorithm started successfully"), 200

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


# 진행률 조회 엔드포인트
@upload_bp.route('/progress', methods=['GET'])
def get_progress():
    return jsonify(progress_status)


@upload_bp.route('/user_videos')
def get_user_videos():
    # 세션에서 로그인 상태를 확인
    loggedInStatus = 'user_id' in session

    if loggedInStatus:
        # 세션에서 user_id 가져오기
        user_id = session['user_id']
        print(f'user_id: {user_id}')

        # 데이터베이스에서 해당 사용자의 모든 영상 조회
        user_videos = Video.query.filter_by(user_id=user_id).all()

        # 조회 결과가 없을 경우
        if not user_videos:
            return jsonify({"videos": []}), 404

        # 영상 데이터를 JSON 형식으로 변환
        videos_data = [
            {
                "video_id": video.id,
                "video_name": video.name,
                "video_date": video.date,
            }
            for video in user_videos
        ]

        return jsonify({"videos": videos_data}), 200
    else:
        # 사용자가 로그인하지 않은 경우
        return jsonify({"error": "User not logged in"}), 401
    


@upload_bp.route('/get_video_url', methods=['POST'])
def get_video_url():
    # JSON 형식으로 데이터 받기
    data = request.json
    video_id = data.get('video_id')
    video_name = data.get('video_name')

    # 사용자 정보 및 경로 설정
    username = getpass.getuser()
    user_path = os.path.join("C:\\Users", username)
    nd_directory = os.path.join(user_path, 'ND')

    # 세션에서 로그인 상태를 확인
    loggedInStatus = 'user_id' in session

    if loggedInStatus:
        # 세션에서 user_id 가져오기
        user_id = session['user_id']
        print(f'user_id: {user_id},{video_id}')

        # video_id를 사용하여 데이터베이스에서 해당 동영상 조회
        video = Video.query.filter_by(id=video_id, user_id=user_id).first()
        if not video:
            return jsonify({"error": "Video not found"}), 404

        # video_name이 None인지 확인
        if not video_name:
            return jsonify({"error": "Video name is missing"}), 400

        # video_id와 video_name을 조합하여 파일명을 생성
        padded_id = str(video_id).zfill(4)
        updated_video_name = video_name.replace(".mp4", "")
        video_dir = f"{padded_id}_{updated_video_name}"
        video_l_name = "Eye_L.mp4"
        video_r_name = "Eye_R.mp4"

        # 결과 파일명 예시
        video_r_l_x = f"{padded_id}_{updated_video_name}_L_X.mp4"
        video_r_l_y = f"{padded_id}_{updated_video_name}_L_Y.mp4"
        video_r_r_x = f"{padded_id}_{updated_video_name}_R_X.mp4"
        video_r_r_y = f"{padded_id}_{updated_video_name}_R_Y.mp4"

        # JSON으로 경로 반환
        return jsonify({
            "video_original_l_url": f"/upload/videos/Original/{video_dir}/{video_l_name}",
            "video_original_r_url": f"/upload/videos/Original/{video_dir}/{video_r_name}",
            "video_result_l_url": f"/upload/videos/Result/{video_dir}/{video_l_name}",
            "video_result_r_url": f"/upload/videos/Result/{video_dir}/{video_r_name}",
            "video_r_l_x": f"/upload/videos/Result/{video_dir}/{video_r_l_x}",
            "video_r_l_y": f"/upload/videos/Result/{video_dir}/{video_r_l_y}",
            "video_r_r_x": f"/upload/videos/Result/{video_dir}/{video_r_r_x}",
            "video_r_r_y": f"/upload/videos/Result/{video_dir}/{video_r_r_y}"
        }), 200
    else:
        # 사용자가 로그인하지 않은 경우
        return jsonify({"error": "User not logged in"}), 401


from flask import send_from_directory, abort
import os
import mimetypes

@upload_bp.route('/upload/videos/<path:subpath>/<path:video_dir>/<path:filename>', methods=['GET'])
def serve_video(subpath, video_dir, filename):
    # 사용자 경로 설정
    username = getpass.getuser()
    user_path = os.path.join("C:\\Users", username, "ND")

    # 요청된 파일 경로 조합
    full_path = os.path.join(user_path, subpath, video_dir, filename)

    # 파일이 실제로 존재하는지 확인
    if not os.path.isfile(full_path):
        print(f"File not found: {full_path}")
        return abort(404)
    
    mime_type, _ = mimetypes.guess_type(full_path)
    if mime_type is None:
        mime_type = 'video/mp4'  # 기본적으로 MP4로 설정

    print(f"Serving file: {full_path} with MIME type: {mime_type}")

    # 디렉토리와 파일명 추출
    directory = os.path.dirname(full_path)
    file_name = os.path.basename(full_path)

    # 파일 제공
    return send_from_directory(directory, file_name)


import subprocess
import os
from flask import jsonify, request

@upload_bp.route('/convert_video', methods=['POST'])
def convert_video():
    data = request.json
    video_path = data.get('video_path')

    # 사용자 경로 및 기본 폴더 설정
    username = getpass.getuser()
    user_path = os.path.join("C:\\Users", username, "ND")

    # HTTP 경로를 로컬 파일 시스템 경로로 변환
    if "/upload/videos/" in video_path:
        video_path = video_path.replace("/upload/videos/", "")

    # 로컬 경로 생성
    local_video_path = os.path.join(user_path, video_path.replace('/', os.path.sep))

    # 디렉토리와 파일명을 유지한 출력 경로 생성
    video_dir = os.path.dirname(local_video_path)
    output_filename = os.path.basename(local_video_path).replace(".mp4", "_converted.mp4")
    output_path = os.path.join(video_dir, output_filename)

    # 이미 변환된 파일이 존재하는지 확인
    if os.path.isfile(output_path):
        print(f"Converted video already exists at: {output_path}")
        relative_path = output_path.replace(user_path, "").lstrip(os.path.sep).replace(os.path.sep, '/')
        converted_video_http_url = f"/upload/videos/{relative_path}"
        return jsonify({"converted_video_path": converted_video_http_url}), 200

    # FFmpeg 명령 실행
    try:
        subprocess.run(
            [
                'ffmpeg',
                '-i', local_video_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-y', output_path
            ],
            check=True
        )
        # 변환된 파일의 HTTP URL 반환
        relative_path = output_path.replace(user_path, "").lstrip(os.path.sep).replace(os.path.sep, '/')
        converted_video_http_url = f"/upload/videos/{relative_path}"
        return jsonify({"converted_video_path": converted_video_http_url}), 200
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return jsonify({"error": "Video conversion failed", "details": str(e)}), 500
