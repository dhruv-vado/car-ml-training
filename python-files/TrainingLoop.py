import tensorflow as tf
from DataGen import DrivingDataGenerator
from modelArch import build_model
import matplotlib.pyplot as plt

# Paths
csv_path = 'controls_optimized.csv'
images_path = 'images'

# Parameters
batch_size = 32
img_shape = (80, 160, 3)

# Generators
train_gen = DrivingDataGenerator(csv_file=csv_path, image_dir=images_path, batch_size=batch_size, augment=True, shuffle=True, img_shape=img_shape)
val_gen = DrivingDataGenerator(csv_file=csv_path, image_dir=images_path, batch_size=batch_size, augment=False, shuffle=False, img_shape=img_shape)  # Ideally a separate val CSV

# Build model
model = build_model(input_shape=img_shape)
model.compile(optimizer='adam', loss='mse')

# Callbacks
early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5)
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2)

# Train
model.fit(train_gen,
          validation_data=val_gen,
          epochs=30,
          callbacks=[early_stop, reduce_lr])
          
history = model.fit(train_gen, validation_data=val_gen, epochs=30, callbacks=[early_stop, reduce_lr])

# Save the model once training is done
model.save('selfdriving_model.h5')

plt.figure(figsize=(8,5))
plt.plot(history.history['loss'], label='Train Loss')
if 'val_loss' in history.history:
    plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Loss Curves')
plt.xlabel('Epoch')
plt.ylabel('Mean Squared Error')
plt.legend()
plt.show()


