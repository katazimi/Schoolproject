import os
import numpy as np
import pandas as pd
import tensorflow as tf

def predict_with_unet(input_array):
    """U-Net 모델을 로드하고 예측을 수행합니다."""
    model_path = os.path.join(os.path.dirname(__file__), "Unet_sharp_model_Rt_Geo_BPPV.h5")
    unet_model = tf.keras.models.load_model(model_path)
    predictions = unet_model.predict(input_array)
    return predictions

def predict_and_preprocess_frames(right_frame_array, left_frame_array, progress_callback=None):
    """프레임 배열을 예측하고 진행 상황을 업데이트합니다."""
    right_frame_array_np = np.array(right_frame_array)
    left_frame_array_np = np.array(left_frame_array)

    reshaped_right_frames = np.reshape(right_frame_array_np, (len(right_frame_array_np), 240, 240, 1))
    reshaped_left_frames = np.reshape(left_frame_array_np, (len(left_frame_array_np), 240, 240, 1))
    
    predicted_right = predict_with_unet(reshaped_right_frames)
    if progress_callback:
        progress_callback(22)

    predicted_left = predict_with_unet(reshaped_left_frames)
    if progress_callback:
        progress_callback(30)

    return predicted_right, predicted_left

def analyze_nystagmus(data_right, data_left):
    """눈의 움직임 데이터를 기반으로 안진(Nystagmus)을 분석합니다."""
    # 오른쪽 눈 데이터 처리
    avg_x_right = data_right['x'].mean()
    avg_y_right = data_right['y'].mean()

    data_right['avg_x'] = avg_x_right
    data_right['avg_y'] = avg_y_right

    std_x_right = data_right['x'].rolling(window=2).std()
    std_y_right = data_right['y'].rolling(window=2).std()
    mean_std_x_right = std_x_right.mean()
    mean_std_y_right = std_y_right.mean()

    max_std_x_right = std_x_right.max()
    threshold_x_right = max_std_x_right / (max_std_x_right - mean_std_x_right)

    max_std_y_right = std_y_right.max()
    threshold_y_right = max_std_y_right / (max_std_y_right - mean_std_y_right)

    data_right['moving_std_x'] = std_x_right
    data_right['moving_std_y'] = std_y_right

    right_x_movement = data_right[(threshold_x_right < data_right['moving_std_x']) & (data_right['moving_std_x'] <= max_std_x_right)]
    right_y_movement = data_right[(threshold_y_right < data_right['moving_std_y']) & (data_right['moving_std_y'] <= max_std_y_right)]

    # 왼쪽 눈 데이터 처리
    avg_x_left = data_left['x'].mean()
    avg_y_left = data_left['y'].mean()
    
    data_left['avg_x'] = avg_x_left
    data_left['avg_y'] = avg_y_left

    std_x_left = data_left['x'].rolling(window=2).std()
    std_y_left = data_left['y'].rolling(window=2).std()
    mean_std_x_left = std_x_left.mean()
    mean_std_y_left = std_y_left.mean()
    
    max_std_x_left = std_x_left.max()
    threshold_x_left = max_std_x_left / (max_std_x_left - mean_std_x_left)
    
    max_std_y_left = std_y_left.max()
    threshold_y_left = max_std_y_left / (max_std_y_left - mean_std_y_left)

    data_left['moving_std_x'] = std_x_left
    data_left['moving_std_y'] = std_y_left

    left_x_movement = data_left[(threshold_x_left < data_left['moving_std_x']) & (data_left['moving_std_x'] <= max_std_x_left)]
    left_y_movement = data_left[(threshold_y_left < data_left['moving_std_y']) & (data_left['moving_std_y'] <= max_std_y_left)]

    df_right_x = pd.merge(right_x_movement, data_right, how='inner')
    df_right_y = pd.merge(right_y_movement, data_right, how='inner')
    df_left_x = pd.merge(left_x_movement, data_left, how='inner')
    df_left_y = pd.merge(left_y_movement, data_left, how='inner')

    return data_right, data_left, df_right_x, df_right_y, df_left_x, df_left_y

def classify_bppv_type(df_right_x, df_right_y, df_left_x, df_left_y, progress_callback=None):
    """안진 데이터를 바탕으로 BPPV 유형을 분류합니다."""
    std_r_x = float(df_right_x['x'].std())
    std_r_y = float(df_right_y['y'].std())
    std_l_x = float(df_left_x['x'].std())
    std_l_y = float(df_left_y['y'].std())
    
    mean_r_x = float(df_right_x['x'].mean())
    mean_r_y = float(df_right_y['y'].mean())    
    mean_l_x = float(df_left_x['x'].mean())
    mean_l_y = float(df_left_y['y'].mean())

    cv_r_x = std_r_x / mean_r_x
    cv_r_y = std_r_y / mean_r_y
    cv_l_x = std_l_x / mean_l_x
    cv_l_y = std_l_y / mean_l_y

    # BPPV 유형 분류
    result_right = 'Horizontal Canal [HC-BPPV]' if cv_r_x > cv_r_y else 'Posterior Canal [PC-BPPV]'
    result_left = 'Horizontal Canal [HC-BPPV]' if cv_l_x > cv_l_y else 'Posterior Canal [PC-BPPV]'

    final_diagnosis = result_right if result_right == result_left else 'Further Analysis Required'

    # 진행 상황 콜백 업데이트
    if progress_callback:
        for i in range(5):
            progress_callback(95 + i)
    
    return final_diagnosis
