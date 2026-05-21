import cv2
import numpy as np
from scipy.signal import find_peaks
from collections import Counter


def detect_grid(image_source, eps=35):
    """
    识别 n*n 颜色块网格。

    参数:
        image_source: 图片路径 或 PIL图像对象 或 numpy数组（BGR格式）
        eps: 颜色聚类阈值（RGB 欧氏距离），默认 35。

    返回:
        size: 网格大小 (cols, rows) - 保证 rows == cols
        color_grid: 二维numpy数组，color_grid[row][col] 对应坐标的颜色序号
    """
    # 处理不同类型的输入
    if isinstance(image_source, str):
        img = cv2.imread(image_source)
        if img is None:
            raise FileNotFoundError(f"无法读取图片: {image_source}")
    elif hasattr(image_source, 'convert'):
        img = cv2.cvtColor(np.array(image_source), cv2.COLOR_RGB2BGR)
    elif isinstance(image_source, np.ndarray):
        img = image_source
    else:
        raise ValueError(f'不支持的图像类型: {type(image_source)}')

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img_rgb.shape[:2]

    # 自动检测背景色（网格线颜色）
    border = np.concatenate([
        img_rgb[0, :, :],
        img_rgb[-1, :, :],
        img_rgb[:, 0, :],
        img_rgb[:, -1, :]
    ])
    bg_color = np.array(Counter([tuple(p) for p in border]).most_common(1)[0][0])

    # 背景掩码 + 行列投影
    pixels = img_rgb.reshape(-1, 3)
    dist_to_bg = np.linalg.norm(pixels.astype(float) - bg_color.astype(float), axis=1)
    bg_mask = (dist_to_bg < 30).reshape(h, w)

    row_proj = np.sum(bg_mask, axis=1)
    col_proj = np.sum(bg_mask, axis=0)

    # 寻峰找网格线
    min_dist = int(min(h, w) * 0.05)
    height_thr = int(max(h, w) * 0.2)
    row_peaks, _ = find_peaks(row_proj, height=height_thr, distance=min_dist)
    col_peaks, _ = find_peaks(col_proj, height=height_thr, distance=min_dist)

    # 计算 n 和每个格子的采样中心
    n = len(row_peaks) + 1
    
    # 如果检测不到，使用默认值
    if n < 4:
        avg_cell_size = int(min(w, h) / 8)
        n = max(4, min(15, round(w / avg_cell_size)))
        row_peaks = np.linspace(h//n, h - h//n, n-1).astype(int)
        col_peaks = np.linspace(w//n, w - w//n, n-1).astype(int)

    row_lines = np.concatenate([[0], row_peaks, [h - 1]])
    col_lines = np.concatenate([[0], col_peaks, [w - 1]])
    row_centers = ((row_lines[:-1] + row_lines[1:]) / 2).astype(int)
    col_centers = ((col_lines[:-1] + col_lines[1:]) / 2).astype(int)

    # 提取每个格子中心颜色（5x5 均值降噪）
    colors = []
    for i in range(n):
        for j in range(n):
            r, c = row_centers[i], col_centers[j]
            r0, r1 = max(0, r - 2), min(h, r + 3)
            c0, c1 = max(0, c - 2), min(w, c + 3)
            patch = img_rgb[r0:r1, c0:c1]
            colors.append(np.mean(patch, axis=(0, 1)))
    colors = np.array(colors)

    # 颜色聚类：在线贪心 + 增量均值更新
    labels = -np.ones(n * n, dtype=int)
    centroids = []

    for idx in range(n * n):
        c = colors[idx]
        if len(centroids) == 0:
            labels[idx] = 0
            centroids.append(c.copy())
        else:
            dists = [np.linalg.norm(c - cent) for cent in centroids]
            min_dist = min(dists)
            nearest = int(np.argmin(dists))
            if min_dist < eps:
                labels[idx] = nearest
                count = np.sum(labels == nearest)
                centroids[nearest] = (centroids[nearest] * (count - 1) + c) / count
            else:
                new_id = len(centroids)
                labels[idx] = new_id
                centroids.append(c.copy())

    # 按首次出现顺序重编号
    seen = {}
    new_labels = -np.ones_like(labels)
    next_id = 0
    for idx in range(n * n):
        old = labels[idx]
        if old not in seen:
            seen[old] = next_id
            next_id += 1
        new_labels[idx] = seen[old]

    num_matrix = new_labels.reshape(n, n)
    num_matrix = np.flip(num_matrix, axis=0)

    return (n, n), num_matrix