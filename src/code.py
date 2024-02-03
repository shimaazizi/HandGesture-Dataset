import gesture_dataset
from PIL import Image
import os
import sklearn
import numpy as np
import matplotlib.pyplot as plt
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from keras.utils import to_categorical

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

# Load the dataset
dataset_path = "/home/shima/Dataset"
output_directory = "dataset"

gesture_dataset.load_dataset(dataset_path, output_directory)

def prepare_dataset(output_directory):
    """
    recognize train_images and train_labels
    """
    train_images = []
    train_labels = []
    unique_image_filenames = set()

    for image_path in os.listdir(output_directory):
        if image_path not in unique_image_filenames:
            image = Image.open(os.path.join(output_directory, image_path))
            image_array = np.array(image)

            # Extract the class name from the image file name
            gesture_class = image_path.split("_")[0]

            train_images.append(image_array)
            train_labels.append(gesture_class)
            unique_image_filenames.add(image_path)

    return train_images, train_labels

        

def display(train_images, train_labels, num_images_to_display):
    """
    Display 4 images before augmentation
    """
    unique_labels = set(train_labels)
    print(f"Unique Labels: {unique_labels}")
    
    # Shuffle and zip images with labels
    shuffled_data = list(zip(train_images, train_labels))
    np.random.shuffle(shuffled_data)
    
    # Extract shuffled images and labels
    shuffled_images, shuffled_labels = zip(*shuffled_data)
    
    # Create a new figure
    fig, axes = plt.subplots(1, num_images_to_display, figsize=(15, 5))

    displayed_labels = set()

    for i, (image, label) in enumerate(zip(shuffled_images, shuffled_labels)):
        if label not in displayed_labels:
            # Display each image in a subplot
            ax = plt.subplot(1, num_images_to_display, len(displayed_labels) + 1)
            ax.imshow(image)
            ax.set_title(f"Label: {label}")
            ax.axis('off')  # Turn off axis labels
            displayed_labels.add(label)

        if len(displayed_labels) == num_images_to_display:
            break

    plt.show()
    plt.tight_layout()

    # Save the figure to a file
    plt.savefig("images.png")
    plt.close()

    

# Prepare the dataset
train_images, train_labels = prepare_dataset(output_directory)
#print(train_images.shape)

# Display the images
display(train_images, train_labels, num_images_to_display=4)

# Resize anb Normalization the images
train_images = np.array([np.array(Image.fromarray(image_array).resize((200, 200))).astype('float32') / 255.0 for image_array in train_images])
print(train_images.shape)

# Convert the labels to a NumPy array
train_labels = np.array(train_labels)

# split train images and validation images
train_images, test_images, train_labels, test_labels = train_test_split(
    train_images, train_labels, test_size=0.2, random_state=42  
)

# Further split the test set into test and validation sets
test_images, val_images, test_labels, val_labels = train_test_split(
    test_images, test_labels, test_size=0.5, random_state=42
)

num_classes = len(set(train_labels))
print(f"Number of classes: {num_classes}")

# one hot encodeing for labels
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical


label_encoder = LabelEncoder()
train_labels_encoded = label_encoder.fit_transform(train_labels)
train_labels_one_hot = to_categorical(train_labels_encoded, num_classes=4)
#print("train_labels_one_hot:")
#print(train_labels_one_hot.shape)

val_labels_encoded = label_encoder.transform(val_labels)
val_labels_one_hot = to_categorical(val_labels_encoded, num_classes=4)
#print("val_labels_one_hot:")
#print(val_labels_one_hot.shape)

train_datagen_augmented = ImageDataGenerator(
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True
)

train_data_augmented = train_datagen_augmented.flow(
    train_images, train_labels_one_hot, batch_size=64, shuffle=False
)
val_datagen_augmented = ImageDataGenerator()  
val_data_augmented = val_datagen_augmented.flow(
    val_images, val_labels_one_hot, batch_size=32, shuffle=False
)


