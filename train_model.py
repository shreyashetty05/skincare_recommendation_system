import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout

# --- Configuration ---
IMG_HEIGHT, IMG_WIDTH = 150, 150  # Target image size
BATCH_SIZE = 32
EPOCHS = 15  # Number of times to train on the entire dataset
TRAIN_DIR = 'dataset/train'
VALIDATION_DIR = 'dataset/validation'

def build_model(num_classes):
    """Builds and compiles the CNN model."""
    model = Sequential([
        # 1st Convolutional Layer
        Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
        MaxPooling2D(2, 2),

        # 2nd Convolutional Layer
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),

        # 3rd Convolutional Layer
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D(2, 2),

        # Flatten the results to feed into a dense layer
        Flatten(),
        
        # Dense Layer for classification
        Dense(512, activation='relu'),
        Dropout(0.5), # Add dropout for regularization to prevent overfitting
        Dense(num_classes, activation='softmax') # Softmax for multi-class classification
    ])

    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    
    return model

def main():
    """Main function to prepare data, train, and save the model."""
    # 1. Prepare Data Generators
    # Rescale pixel values from [0, 255] to [0, 1]
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    validation_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='categorical' # for multi-class classification
    )

    validation_generator = validation_datagen.flow_from_directory(
        VALIDATION_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    # Get the number of classes from the generator
    num_classes = len(train_generator.class_indices)
    print(f"Found {num_classes} classes: {list(train_generator.class_indices.keys())}")

    # 2. Build and Train the Model
    model = build_model(num_classes)
    model.summary() # Print model architecture

    print("\n--- Starting Model Training ---")
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // BATCH_SIZE
    )

    # 3. Save the Trained Model
    print("\n--- Training Complete. Saving model... ---")
    model.save('skin_type_model.h5')
    print("Model saved as skin_type_model.h5")

if __name__ == '__main__':
    main()
