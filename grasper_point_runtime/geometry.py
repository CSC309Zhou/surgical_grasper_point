import math

import cv2
import numpy as np


INPUT_SIZE = 192
HEATMAP_SIZE = 96


def crop_mask(mask, box):
    x1, y1, x2, y2 = box
    margin_x = (x2 - x1) * 0.1
    margin_y = (y2 - y1) * 0.1
    height, width = mask.shape
    left = max(0, math.floor(x1 - margin_x))
    top = max(0, math.floor(y1 - margin_y))
    right = min(width, math.ceil(x2 + margin_x) + 1)
    bottom = min(height, math.ceil(y2 + margin_y) + 1)
    if x2 <= x1 or y2 <= y1 or right <= left or bottom <= top:
        raise ValueError(f"无效的预测框 {box}")

    crop_width, crop_height = right - left, bottom - top
    scale = INPUT_SIZE / max(crop_width, crop_height)
    scaled_width = max(1, round(crop_width * scale))
    scaled_height = max(1, round(crop_height * scale))
    pad_x = (INPUT_SIZE - scaled_width) // 2
    pad_y = (INPUT_SIZE - scaled_height) // 2
    region = np.s_[pad_y:pad_y + scaled_height, pad_x:pad_x + scaled_width]
    canvas = np.zeros((2, INPUT_SIZE, INPUT_SIZE), dtype=np.uint8)
    canvas[0][region] = cv2.resize(
        (mask[top:bottom, left:right] > 0).astype(np.uint8),
        (scaled_width, scaled_height),
        interpolation=cv2.INTER_NEAREST_EXACT,
    )
    canvas[1][region] = 1

    scales = np.array([scaled_width / crop_width, scaled_height / crop_height])
    offsets = np.array([pad_x, pad_y]) + (0.5 - np.array([left, top])) * scales - 0.5
    return canvas, scales, offsets


def box_coordinates(point, box):
    top_left, bottom_right = np.asarray(box).reshape(2, 2)
    return (point - top_left) / (bottom_right - top_left)


def valid_heatmap(canvas):
    block = INPUT_SIZE // HEATMAP_SIZE
    return canvas[1].reshape(HEATMAP_SIZE, block, HEATMAP_SIZE, block).any(axis=(1, 3))
