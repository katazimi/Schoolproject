import os
import cv2
import time
import shutil
import numpy as np
import pandas as pd
from datetime import timedelta
from app import db
from flask import current_app, has_app_context
from sqlalchemy import exists
from ..models import Video, Pupil, KernelLesion
from .analysis import predict_and_preprocess_frames, analyze_nystagmus, classify_bppv_type
from .video_processing import create_folder_paths, process_and_save_frames, process_and_save_annotated_frames
from .plotting import plot_tracking_points, save_bppv_scatter_plot
from .image_processing import preprocess_image, fit_ellipse

class ND:
    def __init__(self):
        print("ND 클래스 초기화")
        super().__init__()
    
    def query_videos(self, user_id):
        # 쿼리 실행
        filtered_videos = Video.query.filter_by(user_id=user_id)
        filtered_videos = filtered_videos.filter(
            ~exists().where(Pupil.video_id == Video.id)
        )
        videos = filtered_videos.all()
        return videos

    def System(self, user_id, progress_callback=None):
        print(f"System 메서드 실행 - user_id: {user_id}")

        try:
            # 현재 애플리케이션 컨텍스트가 없는 경우, 애플리케이션 컨텍스트를 수동으로 설정
            if not has_app_context():
                app = current_app._get_current_object()  # 현재 앱 객체 가져오기
                with app.app_context():
                    videos = self.query_videos(user_id)
            else:
                # 이미 애플리케이션 컨텍스트가 있는 경우, 바로 쿼리 실행
                videos = self.query_videos(user_id)

        except Exception as e:
            print(f"Error executing query: {e}")

        if not videos:
            raise ValueError(f"No video found for user {user_id} that is not linked in Pupil")
        
        for video in videos:
            # 각 video 객체에 대해 원하는 작업 수행
            print(f"Video ID: {video.id}, User ID: {video.user_id}")
            video_name = video.name
            video_path = video.file_path


            # 비디오 ID를 설정
            video_id = f"{video.id}".zfill(4)
            res_id = f"{video_id}_{video_name}"
            updated_res_id = res_id.replace(".mp4", "")
            print(updated_res_id)

            # 폴더 생성 및 경로 설정 -> 5 
            right_original_file, left_original_file, right_result_file, left_result_file, result_directory = create_folder_paths(updated_res_id, progress_callback)

            # 비디오를 읽고 프레임 나누기 -> 15
            fps, total_frames, right_frames, left_frames = process_and_save_frames(
                video_path, right_original_file, left_original_file, progress_callback
            )

            # U-Net 예측 수행 -> 30
            pred_r, pred_l = predict_and_preprocess_frames(right_frames, left_frames, progress_callback)

            # DB에 동공 데이터 삽입-> R:45, L:55
            df_R_pupils= ND.process_ellipse_and_store(
                pred_r, user_id, video_id, video_name, "R", 30, 45, progress_callback
            )
            df_L_pupils = ND.process_ellipse_and_store(
                pred_l, user_id, video_id, video_name, "L", 45, 55, progress_callback
            )
        
            time_list = ND.generate_time_list(fps, total_frames)
            df_R_pupils['time'] = pd.to_datetime(time_list, format='%S.%f', errors='raise')
            df_L_pupils['time'] = pd.to_datetime(time_list, format='%S.%f', errors='raise')   

            progress_callback(60)

            # 결측치 처리
            df_R_pupils['x'] = df_R_pupils['x'].mask(df_R_pupils['x'] <= 0).fillna(0).astype(int)
            df_R_pupils['y'] = df_R_pupils['y'].mask(df_R_pupils['y'] <= 0).fillna(0).astype(int)
            df_L_pupils['x'] = df_L_pupils['x'].mask(df_L_pupils['x'] <= 0).fillna(0).astype(int)
            df_L_pupils['y'] = df_L_pupils['y'].mask(df_L_pupils['y'] <= 0).fillna(0).astype(int)

            progress_callback(62)

            df_L_pupils.to_csv("C:/Users/konyang/Downloads/courses_l.csv")
            df_R_pupils.to_csv("C:/Users/konyang/Downloads/courses_r.csv")

            # Nystagmus 분석 수행
            df_right_pupil, df_left_pupil, df_nystagmus_x_right, df_nystagmus_y_right, df_nystagmus_x_left, df_nystagmus_y_left = analyze_nystagmus(df_R_pupils, df_L_pupils)

            progress_callback(65)

            # 이동 평균 편차 그래프 
            plot_tracking_points(df_right_pupil, df_left_pupil, updated_res_id, result_directory)

            progress_callback(75)

            # 영상 위에 오버레이 -> 85
            process_and_save_annotated_frames(video_path, right_original_file, left_original_file, df_right_pupil, df_left_pupil, progress_callback)

            # 산점도 -> 95
            ND.process_eye_videos(right_result_file, left_result_file, df_right_pupil, df_left_pupil, result_directory, fps, (465,462), progress_callback)

            # 분석 결과를 바탕으로 추가 정보 저장
            kernel = classify_bppv_type(df_nystagmus_x_right, df_nystagmus_y_right, df_nystagmus_x_left, df_nystagmus_y_left, progress_callback)

            # DB에 분석 결과 저장
            new_lesion = KernelLesion(video_id=video_id, kernellesion=kernel, user_id=user_id)
            db.session.add(new_lesion)
            db.session.commit()

            print(f"Analysis for {video_name} completed and saved.")

        if progress_callback:
            progress_callback(100)

    def process_ellipse_and_store(image_array, user_id, video_id, video_name, side, progress_start, progress_end, progress_callback=None):
        """이미지 배열에서 타원을 검출하고 데이터베이스에 저장하고, x와 y 값을 데이터프레임에 저장합니다."""
        import pandas as pd

        results = []
        try:
            for i, image in enumerate(image_array):
                frame_number = f'{i+1:04d}'
                image_name = f"{video_id}_{video_name}_{side}_{frame_number}"

                preprocessed_contour = preprocess_image(image)
                refined_contour = np.delete(preprocessed_contour, [0, 1, -2, -1], axis=0)

                # 윤곽선의 점 개수가 부족할 경우 기본값으로 저장
                if len(refined_contour) < 5:
                    new_pupil = Pupil(imageid=image_name, x=0, y=0, max_distance=0, min_distance=0, slope=0, video_id=video_id, user_id=user_id)
                    db.session.add(new_pupil)
                    db.session.commit()
                    results.append({'imageid': image_name, 'x': 0, 'y': 0})
                    continue

                # 타원 맞추기
                ellipse_parameters = fit_ellipse(refined_contour)
                center_x, center_y = ellipse_parameters[0]
                axis_x, axis_y = ellipse_parameters[1]
                angle = ellipse_parameters[2]

                # SQLAlchemy를 사용하여 데이터베이스에 삽입
                new_pupil = Pupil(imageid=image_name, x=center_x, y=center_y, max_distance=axis_x, min_distance=axis_y, slope=angle, video_id=video_id, user_id=user_id)
                db.session.add(new_pupil)
                db.session.commit()

                # 결과를 리스트에 저장 (데이터프레임 생성용)
                results.append({'imageid': image_name, 'x': center_x, 'y': center_y})

                # 진행 상황 업데이트
                if progress_callback:
                    progress_percent = progress_start + int((i + 1) / len(image_array) * (progress_end - progress_start))
                    progress_callback(progress_percent)

                time.sleep(0.001)
        except Exception as e:
            db.session.rollback()  # 오류 발생 시 롤백
            print(f"Error processing ellipse and storing data: {e}")

        # x와 y 값을 데이터프레임에 저장
        df_pupils = pd.DataFrame(results, columns=['imageid', 'x', 'y'])
        return df_pupils
    
    

    def generate_time_list(fps, total_frames):
        time_list = []

        for current_frame in range(int(total_frames)):
            duration_seconds = current_frame / fps if fps > 0 else 0
            time_delta = timedelta(seconds=duration_seconds)
            time_str = str(time_delta.total_seconds())
            time_list.append(time_str)
        
        return time_list




    def process_eye_videos(right_eye_result_video_path, left_eye_result_video_path, right_eye_data, left_eye_data, result_directory, frames_per_second, video_resolution, progress_callback):
        # Create video writers
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        right_eye_video_writer = cv2.VideoWriter(right_eye_result_video_path, fourcc, frames_per_second, video_resolution)
        left_eye_video_writer = cv2.VideoWriter(left_eye_result_video_path, fourcc, frames_per_second, video_resolution)

        # Define image result path
        image_result_path = os.path.join(result_directory, 'img')

        # Process right eye video
        if not os.path.exists(image_result_path):
            os.makedirs(image_result_path)
        for i in range(len(right_eye_data)):
            save_bppv_scatter_plot(right_eye_data[:i+1], image_result_path, "Eye_R", i+1, 85, 90, progress_callback)
        for i in range(len(right_eye_data)):
            image_path = os.path.join(image_result_path, f"{i+1}.png")
            color_image = cv2.imread(image_path)
            right_eye_video_writer.write(color_image)
        right_eye_video_writer.release()
        shutil.rmtree(image_result_path)

        # Process left eye video
        if not os.path.exists(image_result_path):
            os.makedirs(image_result_path)
        for i in range(len(left_eye_data)):
            save_bppv_scatter_plot(left_eye_data[:i+1], image_result_path, "Eye_L", i+1, 90, 95, progress_callback)
        for i in range(len(left_eye_data)):
            image_path = os.path.join(image_result_path, f"{i+1}.png")
            color_image = cv2.imread(image_path)
            left_eye_video_writer.write(color_image)
        left_eye_video_writer.release()
        shutil.rmtree(image_result_path)