import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.applications import MobileNetV2

# --- Configuration ---
IMG_HEIGHT, IMG_WIDTH = 150, 150  # Target image size
BATCH_SIZE = 4  # Reduced batch size suitable for small datasets
EPOCHS = 15      # Epochs for training the new 'head' of the model
TRAIN_DIR = 'dataset/train'
VALIDATION_DIR = 'dataset/validation'

def build_model(num_classes):
    """
    Builds a model using MobileNetV2 for transfer learning.
    This is much more effective for small datasets.
    """
    # Load the MobileNetV2 model, pre-trained on ImageNet, without the top classification layer
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)
    )

    # Freeze the layers of the base model so they don't get updated during training
    base_model.trainable = False

    # Create our new model 'head'
    # Start with the output of the base model
    x = base_model.output
    # Add a pooling layer to reduce dimensions
    x = GlobalAveragePooling2D()(x)
    # Add a dense layer with dropout for classification
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    # Final output layer with softmax for our classes
    predictions = Dense(num_classes, activation='softmax')(x)

    # This is the final model we will train
    model = Model(inputs=base_model.input, outputs=predictions)

    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    return model

def main():
    """Main function to prepare data, train, and save the model."""
    # 1. Prepare Data Generators (with preprocessing for MobileNetV2)
    train_datagen = ImageDataGenerator(
        preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    validation_datagen = ImageDataGenerator(
        preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input
    )

    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    validation_generator = validation_datagen.flow_from_directory(
        VALIDATION_DIR,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    num_classes = len(train_generator.class_indices)
    print(f"Found {num_classes} classes: {list(train_generator.class_indices.keys())}")

    # 2. Build and Train the Model
    model = build_model(num_classes)
    model.summary()

    print("\n--- Starting Model Training ---")
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=validation_generator,
    )

    # 3. Save the Trained Model
    print("\n--- Training Complete. Saving model... ---")
    # CRITICAL FIX: Changed filename from .hsil to .h5 to match app.py
    model.save('skin_type_model.h5')
    print("Model saved as skin_type_model.h5")

if __name__ == '__main__':
    main()

