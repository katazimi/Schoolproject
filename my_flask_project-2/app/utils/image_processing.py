import numpy as np
import cv2

def crop_image(image):
    """이미지를 자르고 정규화된 이미지를 반환합니다."""
    cropped_image = image[:, 40:280]
    normalized_image = np.array(cropped_image)
    return normalized_image.astype(np.uint8), normalized_image / 255

def preprocess_image(image):
    """이미지를 전처리하고 가장 큰 윤곽선을 반환합니다."""
    reshaped_image = np.reshape(image, (240, 240))
    uint8_image = (reshaped_image * 255).astype(np.uint8)
    _, binary_image = cv2.threshold(uint8_image, 0, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    _, _, largest_contour_index = find_largest_contour(contours)
    largest_contour = contours[largest_contour_index]
    reshaped_contour = largest_contour.reshape(largest_contour.shape[0], largest_contour.shape[2])
    return reshaped_contour

def find_largest_contour(contours):
    """가장 큰 2D 배열을 가진 윤곽선을 찾습니다."""
    max_element_count = -1
    largest_contour = None
    largest_contour_index = -1
    
    for index, contour in enumerate(contours):
        element_count = sum(len(row) for row in contour)
        if element_count > max_element_count:
            max_element_count = element_count
            largest_contour = contour
            largest_contour_index = index
    return largest_contour, max_element_count, largest_contour_index

def fit_ellipse(contour):
    """윤곽선을 이용해 타원을 맞춥니다."""
    return cv2.fitEllipse(contour)
