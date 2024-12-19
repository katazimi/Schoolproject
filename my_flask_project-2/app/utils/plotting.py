import os
import numpy as np
import pandas as pd
import datetime
import matplotlib
matplotlib.use('Agg')  # GUI가 필요 없는 백엔드 사용
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FFMpegWriter, FuncAnimation
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Mac에서는 'AppleGothic', Windows에서는 'Malgun Gothic' 사용
plt.rcParams['axes.unicode_minus'] = False   # 마이너스 기호 깨짐 방지

def plot_tracking_points(data_r, data_l, res_id, path, fps=30):
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    fig3, ax3 = plt.subplots()
    fig4, ax4 = plt.subplots()

    # X축 눈금 설정: 초 단위로 표시되도록 설정
    time_formatter = plt.FuncFormatter(lambda x, pos: f"{int(x / fps):02d}")

    # 각 subplot에 설정 적용
    ax1.set_ylim(0, 320)
    ax1.set_ylabel('X_point')
    ax1.set_xlabel('time(s)')
    ax1.xaxis.set_major_locator(plt.MultipleLocator(30))
    ax1.xaxis.set_major_formatter(time_formatter)

    ax2.set_ylim(0, 240)
    ax2.set_ylabel('Y_point')
    ax2.set_xlabel('time(s)')
    ax2.xaxis.set_major_locator(plt.MultipleLocator(30))
    ax2.xaxis.set_major_formatter(time_formatter)

    ax3.set_ylim(0, 320)
    ax3.set_ylabel('X_point')
    ax3.set_xlabel('time(s)')
    ax3.xaxis.set_major_locator(plt.MultipleLocator(30))
    ax3.xaxis.set_major_formatter(time_formatter)

    ax4.set_ylim(0, 240)
    ax4.set_ylabel('Y_point')
    ax4.set_xlabel('time(s)')
    ax4.xaxis.set_major_locator(plt.MultipleLocator(30))
    ax4.xaxis.set_major_formatter(time_formatter)

    interval = int(1000 / fps)

    global ani1, ani2, ani3, ani4

    def update(frame_idx):
        # fig1: 오른쪽 눈의 X 좌표
        ax1.clear()
        ax1.set_ylim(0, 320)
        ax1.set_ylabel('X_point')
        ax1.set_xlabel('time(s)')
        ax1.xaxis.set_major_locator(plt.MultipleLocator(30))
        ax1.xaxis.set_major_formatter(time_formatter)

        movstd_diff_squared_x = np.diff(data_r['moving_std_x'][:frame_idx], prepend=0) ** 3 * 3
        movstd_diff_squared_x = np.where(movstd_diff_squared_x < data_r['avg_x'][:frame_idx], 0, movstd_diff_squared_x)
        
        # 처음 5개의 데이터를 0으로 설정
        movstd_diff_squared_x[:5] = 0
        
        for i in range(1, frame_idx):
            color = 'red' if movstd_diff_squared_x[i] != 0 else 'green'
            ax1.plot(data_r['time'][i-1:i+1], data_r['x'][i-1:i+1], color=color)
        
        # 빨간 구간을 찾아 배경에 강조 표시 (연속된 0이 아닌 구간)
        non_zero_regions = np.where(movstd_diff_squared_x != 0)[0]
        if len(non_zero_regions) > 0:
            start_idx = non_zero_regions[0]
            for i in range(1, len(non_zero_regions)):
                if non_zero_regions[i] != non_zero_regions[i-1] + 1:
                    ax1.axvspan(data_r['time'][start_idx], data_r['time'][non_zero_regions[i-1]], color='red', alpha=0.3)
                    start_idx = non_zero_regions[i]
            ax1.axvspan(data_r['time'][start_idx], data_r['time'][non_zero_regions[-1]], color='red', alpha=0.3, label='안진 의심')
        
        ax1.plot([], [], color='green', label='오른쪽눈 X좌표')
        ax1.plot(data_r['time'][:frame_idx], data_r['avg_x'][:frame_idx], c="grey", label='좌표 평균')
        ax1.plot(data_r['time'][:frame_idx], data_r['moving_std_x'][:frame_idx], color='red', label='이동 표준편차')
        
        ax1.legend()

        # fig2: 오른쪽 눈의 Y 좌표
        ax2.clear()
        ax2.set_ylim(0, 240)
        ax2.set_ylabel('Y_point')
        ax2.set_xlabel('time(s)')
        ax2.xaxis.set_major_locator(plt.MultipleLocator(30))
        ax2.xaxis.set_major_formatter(time_formatter)

        movstd_diff_squared_y = np.diff(data_r['moving_std_y'][:frame_idx], prepend=0) ** 3 * 3
        movstd_diff_squared_y = np.where(movstd_diff_squared_y < data_r['avg_y'][:frame_idx], 0, movstd_diff_squared_y)

        # 처음 5개의 데이터를 0으로 설정
        movstd_diff_squared_y[:5] = 0

        for i in range(1, frame_idx):
            color = 'red' if movstd_diff_squared_y[i] != 0 else 'green'
            ax2.plot(data_r['time'][i-1:i+1], data_r['y'][i-1:i+1], color=color)
        
        non_zero_regions = np.where(movstd_diff_squared_y != 0)[0]
        if len(non_zero_regions) > 0:
            start_idx = non_zero_regions[0]
            for i in range(1, len(non_zero_regions)):
                if non_zero_regions[i] != non_zero_regions[i-1] + 1:
                    ax2.axvspan(data_r['time'][start_idx], data_r['time'][non_zero_regions[i-1]], color='red', alpha=0.3)
                    start_idx = non_zero_regions[i]
            ax2.axvspan(data_r['time'][start_idx], data_r['time'][non_zero_regions[-1]], color='red', alpha=0.3, label='안진 의심')
        
        ax2.plot([], [], color='green', label='오른쪽눈 Y좌표')
        ax2.plot(data_r['time'][:frame_idx], data_r['avg_y'][:frame_idx], c="grey", label='좌표 평균')
        ax2.plot(data_r['time'][:frame_idx], data_r['moving_std_y'][:frame_idx], color='red', label='이동 표준편차')
        
        ax2.legend()

        # fig3: 왼쪽 눈의 X 좌표
        ax3.clear()
        ax3.set_ylim(0, 320)
        ax3.set_ylabel('X_point')
        ax3.set_xlabel('time(s)')
        ax3.xaxis.set_major_locator(plt.MultipleLocator(30))
        ax3.xaxis.set_major_formatter(time_formatter)

        movstd_diff_squared_x_l = np.diff(data_l['moving_std_x'][:frame_idx], prepend=0) ** 2 * 3
        movstd_diff_squared_x_l = np.where(movstd_diff_squared_x_l < data_l['avg_x'][:frame_idx], 0, movstd_diff_squared_x_l)

        # 처음 5개의 데이터를 0으로 설정
        movstd_diff_squared_x_l[:5] = 0

        for i in range(1, frame_idx):
            color = 'red' if movstd_diff_squared_x_l[i] != 0 else 'green'
            ax3.plot(data_l['time'][i-1:i+1], data_l['x'][i-1:i+1], color=color)
        
        non_zero_regions = np.where(movstd_diff_squared_x_l != 0)[0]
        if len(non_zero_regions) > 0:
            start_idx = non_zero_regions[0]
            for i in range(1, len(non_zero_regions)):
                if non_zero_regions[i] != non_zero_regions[i-1] + 1:
                    ax3.axvspan(data_l['time'][start_idx], data_l['time'][non_zero_regions[i-1]], color='red', alpha=0.3)
                    start_idx = non_zero_regions[i]
            ax3.axvspan(data_l['time'][start_idx], data_l['time'][non_zero_regions[-1]], color='red', alpha=0.3, label='안진 의심')
        
        ax3.plot([], [], color='green', label='왼쪽눈 X좌표')
        ax3.plot(data_l['time'][:frame_idx], data_l['avg_x'][:frame_idx], c="grey", label='좌표 평균')
        ax3.plot(data_l['time'][:frame_idx], data_l['moving_std_x'][:frame_idx], color='red', label='이동 표준편차')
        
        ax3.legend()

        # fig4: 왼쪽 눈의 Y 좌표
        ax4.clear()
        ax4.set_ylim(0, 240)
        ax4.set_ylabel('Y_point')
        ax4.set_xlabel('time(s)')
        ax4.xaxis.set_major_locator(plt.MultipleLocator(30))
        ax4.xaxis.set_major_formatter(time_formatter)

        movstd_diff_squared_y_l = np.diff(data_l['moving_std_y'][:frame_idx], prepend=0) ** 2 * 3
        movstd_diff_squared_y_l = np.where(movstd_diff_squared_y_l < data_l['avg_y'][:frame_idx], 0, movstd_diff_squared_y_l)

        # 처음 5개의 데이터를 0으로 설정
        movstd_diff_squared_y_l[:5] = 0

        for i in range(1, frame_idx):
            color = 'red' if movstd_diff_squared_y_l[i] != 0 else 'green'
            ax4.plot(data_l['time'][i-1:i+1], data_l['y'][i-1:i+1], color=color)
        
        non_zero_regions = np.where(movstd_diff_squared_y_l != 0)[0]
        if len(non_zero_regions) > 0:
            start_idx = non_zero_regions[0]
            for i in range(1, len(non_zero_regions)):
                if non_zero_regions[i] != non_zero_regions[i-1] + 1:
                    ax4.axvspan(data_l['time'][start_idx], data_l['time'][non_zero_regions[i-1]], color='red', alpha=0.3)
                    start_idx = non_zero_regions[i]
            ax4.axvspan(data_l['time'][start_idx], data_l['time'][non_zero_regions[-1]], color='red', alpha=0.3, label='안진 의심')
        
        ax4.plot([], [], color='green', label='왼쪽눈 Y좌표')
        ax4.plot(data_l['time'][:frame_idx], data_l['avg_y'][:frame_idx], c="grey", label='좌표 평균')
        ax4.plot(data_l['time'][:frame_idx], data_l['moving_std_y'][:frame_idx], color='red', label='이동 표준편차')
        
        ax4.legend()

    writer = FFMpegWriter(fps=30)

    global ani1, ani2, ani3, ani4
    ani1 = FuncAnimation(fig1, update, frames=len(data_r), repeat=False, interval=interval)
    ani2 = FuncAnimation(fig2, update, frames=len(data_r), repeat=False, interval=interval)
    ani3 = FuncAnimation(fig3, update, frames=len(data_r), repeat=False, interval=interval)
    ani4 = FuncAnimation(fig4, update, frames=len(data_r), repeat=False, interval=interval)

    video_path1 = os.path.join(path, f"{res_id}_R_X.mp4")
    video_path2 = os.path.join(path, f"{res_id}_R_Y.mp4")
    video_path3 = os.path.join(path, f"{res_id}_L_X.mp4")
    video_path4 = os.path.join(path, f"{res_id}_L_Y.mp4")

    ani1.save(video_path1, writer=writer)
    ani2.save(video_path2, writer=writer)
    ani3.save(video_path3, writer=writer)
    ani4.save(video_path4, writer=writer)

    plt.close(fig1) 
    plt.close(fig2) 
    plt.close(fig3) 
    plt.close(fig4)



def save_bppv_scatter_plot(df, output_path, label, index, progress_start, progress_end, progress_callback=None):
    """BPPV 데이터를 산점도로 플로팅하고 이미지를 저장합니다."""
    image_path = os.path.join(output_path, f"{index}.png")

    fig, ax = plt.subplots(figsize=(6, 6))

    # 플롯 설정
    ax.set_xlim([0, 240])
    ax.set_ylim([240, 0])
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.axis('off')

    # 산점도 그리기
    ax.scatter('x', 'y', data=df, color="blue", label=label, s=25)
    ax.legend()

    # 이미지 저장
    fig.savefig(image_path, bbox_inches='tight', pad_inches=0)

    # 진행 상황 콜백 업데이트
    if progress_callback:
        progress_percent = progress_start + int((index + 1) / len(df) * (progress_end - progress_start))
        progress_callback(progress_percent)

    plt.close(fig) 