import tensorflow as tf
import numpy as np
import cv2
import pandas as pd
import random
from tensorflow.keras.utils import Sequence

class DrivingDataGenerator(Sequence):
    def __init__(self, csv_file, image_dir, batch_size=32, augment=True, shuffle=True, img_shape=(160, 80, 3)):
        self.df = pd.read_csv(csv_file)
        self.image_dir = image_dir
        self.batch_size = batch_size
        self.augment = augment
        self.shuffle = shuffle
        self.img_shape = img_shape
        self.indexes = np.arange(len(self.df))
        self.on_epoch_end()
        
    def __len__(self):
        return int(np.floor(len(self.df) / self.batch_size))
    
    def __getitem__(self, index):
        # Generate indexes for the batch
        batch_inds = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        batch_data = self.df.iloc[batch_inds]
        
        images = np.zeros((self.batch_size, *self.img_shape), dtype=np.float32)
        controls = np.zeros((self.batch_size, 3), dtype=np.float32)  # [steer, throttle, brake]
        
        for i, (_, row) in enumerate(batch_data.iterrows()):
            img_path = f"{self.image_dir}/{row['center_frame']}"
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (self.img_shape[1], self.img_shape[0]))
            
            steer, throttle, brake = row['steer'], row['throttle'], row['brake']
            
            if self.augment:
                img, steer = self.augment_image(img, steer)
            
            img = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)  # <-- Convert here
            img = img / 255.0                            # <-- Normalize here
            
            images[i] = img
            controls[i] = [steer, throttle, brake]
        
        return images, controls
    
    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indexes)
    
    def augment_image(self, img, steer):
        # Random brightness augmentation
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        ratio = 1.0 + 0.4*(random.random() - 0.5)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * ratio, 0, 255)
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        
        # Random horizontal flip
        if random.random() < 0.5:
            img = cv2.flip(img, 1)
            steer = -steer
        
        # Random translation along x-axis
        if random.random() < 0.5:
            tr_x = random.randint(-20, 20)
            steer += tr_x * 0.005  # tuning factor
            trans_mat = np.float32([[1, 0, tr_x], [0, 1, 0]])
            img = cv2.warpAffine(img, trans_mat, (img.shape[1], img.shape[0]))
        
        return img, steer
