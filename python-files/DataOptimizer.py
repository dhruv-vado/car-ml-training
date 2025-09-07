import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Adjust these paths as needed:
INPUT_CSV = 'controls_cleaned.csv'
OUTPUT_CSV = 'controls_optimized.csv'

# Settings
ZERO_STEAR_TOLERANCE = 1e-3      # what counts as 'zero' steering
KEEP_ZERO_STEER_FRAC = 0.1       # keep ~10% of zero-steering examples

# 1. Load data
df = pd.read_csv(INPUT_CSV)

# 2. Plot original steering distribution (optional)
plt.figure(figsize=(10,5))
plt.hist(df['steer'], bins=50, color='blue', alpha=0.7)
plt.title('Steering Angle Distribution (Before)')
plt.xlabel('Steering Angle')
plt.ylabel('Frame Count')
plt.show()

# 3. Create flag for (near-)zero steer
df['is_zero_steer'] = df['steer'].abs() < ZERO_STEAR_TOLERANCE

zero_steer_df = df[df['is_zero_steer']]
non_zero_steer_df = df[~df['is_zero_steer']]

# 4. Downsample zero-steering frames
zero_steer_sample = zero_steer_df.sample(frac=KEEP_ZERO_STEER_FRAC, random_state=42)
optimized_df = pd.concat([non_zero_steer_df, zero_steer_sample], ignore_index=True)

# 5. Shuffle and drop helper column
optimized_df = optimized_df.sample(frac=1, random_state=42).reset_index(drop=True)
optimized_df = optimized_df.drop(columns=['is_zero_steer'])

# 6. Plot new steering distribution (optional)
plt.figure(figsize=(10,5))
plt.hist(optimized_df['steer'], bins=50, color='green', alpha=0.7)
plt.title('Steering Angle Distribution (After Optimization)')
plt.xlabel('Steering Angle')
plt.ylabel('Frame Count')
plt.show()

# 7. Save to new CSV
optimized_df.to_csv(OUTPUT_CSV, index=False)

print(f"Original frame count: {len(df)}")
print(f"Optimized frame count: {len(optimized_df)}")
print("Saved as:", OUTPUT_CSV)
