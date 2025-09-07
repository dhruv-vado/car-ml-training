import cv2
import numpy as np
import random

def augment_image(img, steer, flip_prob=0.5):
    # 1. Random brightness
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    ratio = 1.0 + 0.4 * (np.random.rand() - 0.5)
    hsv[:,:,2] = np.clip(hsv[:,:,2] * ratio, 0, 255)
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    # 2. Random blur
    if random.random() < 0.2:
        k = random.choice([3, 5])
        img = cv2.GaussianBlur(img, (k, k), 0)

    # 3. Random X translation
    if random.random() < 0.5:
        dx = np.random.randint(-30, 30)
        steer += dx / 100.0  # Empirical adjustment
        M = np.float32([[1, 0, dx], [0, 1, 0]])
        img = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))

    # 4. Horizontal flip
    if random.random() < flip_prob:
        img = cv2.flip(img, 1)
        steer = -steer

    # 5. Random shadow
    if random.random() < 0.3:
        x1, x2 = np.random.randint(0, img.shape[1], 2)
        mask = np.zeros_like(img, dtype=np.uint8)
        c = np.random.uniform(0.4, 0.7)
        cv2.line(mask, (x1,0), (x2,img.shape[0]), (1,1,1), 60)
        img = cv2.addWeighted(img, c, mask, 1-c, 0)

    return img, steer
