import os
import cv2
import pandas as pd
import numpy as np

# Paths (edit as needed)
IMAGES_DIR = 'images'
INPUT_CSV = 'controls.csv'
OUTPUT_CSV = 'controls_cleaned.csv'

def is_image_valid(image_path):
    """Check if an image file exists and can be read by OpenCV."""
    if not os.path.isfile(image_path):
        return False
    img = cv2.imread(image_path)
    if img is None:
        return False
    return True

def remove_invalid_rows(df):
    """Remove rows with invalid or NaN control values or out-of-range values."""
    # Drop rows with NaN
    df = df.dropna(subset=['steer', 'throttle', 'brake'])
    # Remove infinite values
    df = df[np.isfinite(df['steer'])]
    df = df[np.isfinite(df['throttle'])]
    df = df[np.isfinite(df['brake'])]
    # Clamp within expected physical bounds
    df = df[(df['steer'] >= -1.0) & (df['steer'] <= 1.0)]
    df = df[(df['throttle'] >= 0.0) & (df['throttle'] <= 1.0)]
    df = df[(df['brake'] >= 0.0) & (df['brake'] <= 1.0)]
    return df

def remove_duplicates(df):
    """Remove duplicate rows (exact duplicates)."""
    return df.drop_duplicates()

def remove_idle_frames(df):
    """
    Remove frames where the car is basically idle:
    No steering, no throttle, no brake.
    These frames add no learning signal.
    """
    idle_mask = (df['steer'].abs() < 1e-3) & (df['throttle'] < 1e-3) & (df['brake'] < 1e-3)
    return df[~idle_mask]

def check_images_exist(df):
    """Keep only rows where all image files exist and are valid."""
    def all_images_exist(row):
        files = [row['center_frame'], row['left_frame'], row['right_frame']]
        return all(is_image_valid(os.path.join(IMAGES_DIR, f)) for f in files)

    exist_mask = df.apply(all_images_exist, axis=1)
    print(f"Removing {len(df) - exist_mask.sum()} rows with missing/corrupt images")
    return df[exist_mask]

def main():
    print("Loading data...")
    df = pd.read_csv(INPUT_CSV)

    print(f"Original dataset size: {len(df)}")

    # 1. Remove rows with missing or corrupt images
    df = check_images_exist(df)

    # 2. Remove invalid control values
    df = remove_invalid_rows(df)

    # 3. Remove duplicates
    df = remove_duplicates(df)

    # 4. Remove idle frames (no action)
    df = remove_idle_frames(df)

    print(f"Cleaned dataset size: {len(df)}")

    # Save cleaned CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Clean dataset saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
