import os
import cv2
import getpass
from .image_processing import crop_image

def create_folder_paths(base_name, progress_callback=None):
    """파일 경로를 생성하고 필요한 폴더를 만듭니다."""
    username = getpass.getuser()
    user_path = os.path.join("C:\\Users", username)
    nd_directory = os.path.join(user_path, 'ND')

    # Original과 Result 폴더 경로 설정
    original_directory = os.path.join(nd_directory, 'Original', base_name)
    result_directory = os.path.join(nd_directory, 'Result', base_name)

    # 각 파일 경로 설정
    right_original_file = os.path.join(original_directory, 'Eye_R.mp4')
    left_original_file = os.path.join(original_directory, 'Eye_L.mp4')
    right_result_file = os.path.join(result_directory, 'Eye_R.mp4')
    left_result_file = os.path.join(result_directory, 'Eye_L.mp4')

    # 필요한 디렉터리 생성
    os.makedirs(original_directory, exist_ok=True)
    os.makedirs(result_directory, exist_ok=True)

    if progress_callback:
            progress_callback(5)

    return right_original_file, left_original_file, right_result_file, left_result_file, result_directory

def process_and_save_frames(video_path, right_output_path, left_output_path, progress_callback=None):
    """비디오를 읽고, 프레임을 잘라 저장합니다."""
    frame_size = (240, 240)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_capture = cv2.VideoCapture(video_path)

    if not video_capture.isOpened():
        print("Could not open:", video_path)
        return

    fps = video_capture.get(cv2.CAP_PROP_FPS)
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    # 비디오 작성기 초기화
    right_writer = cv2.VideoWriter(right_output_path, fourcc, fps, frame_size)
    left_writer = cv2.VideoWriter(left_output_path, fourcc, fps, frame_size)

    right_frames = []
    left_frames = []

    for frame_index in range(total_frames):
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to read frame.")
            break

        # 그레이스케일 변환 및 프레임 분할
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        right_frame = cv2.resize(gray_frame[:, :161], (320, 240))
        left_frame = cv2.resize(gray_frame[:, 161:], (320, 240))

        # 프레임 잘라내기 및 정규화
        cropped_right, right_normalized = crop_image(right_frame)
        cropped_left, left_normalized = crop_image(left_frame)

        # 컬러 변환
        color_right_frame = cv2.cvtColor(cropped_right, cv2.COLOR_GRAY2RGB)
        color_left_frame = cv2.cvtColor(cropped_left, cv2.COLOR_GRAY2RGB)

        # 비디오에 프레임 저장
        right_writer.write(color_right_frame)
        left_writer.write(color_left_frame)

        right_frames.append(right_normalized)
        left_frames.append(left_normalized)

        # 진행 상황 콜백 업데이트
        if progress_callback:
            progress_callback(5 + (10 * frame_index / total_frames))

    video_capture.release()
    right_writer.release()
    left_writer.release()

    return fps, total_frames, right_frames, left_frames

def process_and_save_annotated_frames(video_path, right_output_path, left_output_path, right_data, left_data, progress_callback=None):
    """프레임을 읽고 좌표에 따라 점을 추가한 후 저장합니다."""
    frame_size = (240, 240)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # 좌표 데이터를 리스트로 변환
    right_points = right_data[['x', 'y']].values.tolist()
    left_points = left_data[['x', 'y']].values.tolist()

    video_capture = cv2.VideoCapture(video_path)

    if not video_capture.isOpened():
        print("Could not open:", video_path)
        return

    fps = video_capture.get(cv2.CAP_PROP_FPS)
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    # 비디오 작성기 초기화
    right_writer = cv2.VideoWriter(right_output_path, fourcc, fps, frame_size)
    left_writer = cv2.VideoWriter(left_output_path, fourcc, fps, frame_size)

    for frame_index in range(total_frames):
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to read frame.")
            break

        # 그레이스케일 변환 및 프레임 분할
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        right_frame = cv2.resize(gray_frame[:, :161], (320, 240))
        left_frame = cv2.resize(gray_frame[:, 161:], (320, 240))

        # 프레임 잘라내기 및 정규화
        cropped_right, right_normalized = crop_image(right_frame)
        cropped_left, left_normalized = crop_image(left_frame)

        # 컬러 변환
        color_right_frame = cv2.cvtColor(cropped_right, cv2.COLOR_GRAY2RGB)
        color_left_frame = cv2.cvtColor(cropped_left, cv2.COLOR_GRAY2RGB)

        # 좌표에 점 추가
        if frame_index < len(left_points):
            x_l, y_l = left_points[frame_index]
            cv2.circle(color_left_frame, (int(x_l), int(y_l)), 5, (255, 0, 0), -1)  # 왼쪽 프레임에 빨간색 점 추가

        if frame_index < len(right_points):
            x_r, y_r = right_points[frame_index]
            cv2.circle(color_right_frame, (int(x_r), int(y_r)), 5, (255, 0, 0), -1)  # 오른쪽 프레임에 빨간색 점 추가

        # 비디오에 프레임 저장
        right_writer.write(color_right_frame)
        left_writer.write(color_left_frame)

        # 진행 상황 콜백 업데이트
        if progress_callback:
            progress_callback(75 + (10 * frame_index / total_frames))

    video_capture.release()
    right_writer.release()
    left_writer.release()