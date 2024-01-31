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


    for image_path in os.listdir(output_directory):
        image = Image.open(os.path.join(output_directory, image_path))
        image_array = np.array(image)
        train_images.append(image_array)
        train_labels.append(image_path.split("_")[0])
        
    return train_images, train_labels
        

def display(train_images, train_labels, num_images_to_display):
    """""
    Display 4 images before augmentation

    """
    # shuffle
    train_images, train_labels = shuffle(train_images, train_labels, random_state=42)
    # Create a new figure
    fig, axes = plt.subplots(1, num_images_to_display, figsize=(15, 5))

    for i in range(num_images_to_display):
    # Display each image in a subplot
        ax = plt.subplot(1, num_images_to_display, i + 1)
        ax.imshow(train_images[i])
        ax.set_title(f"Label: {train_labels[i]}")
        ax.axis('off')  # Turn off axis labels
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
#print(train_images.shape)

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



#  create model 


model = models.Sequential()
model.add(layers.Conv2D(10, (3, 3), activation='relu', input_shape=(200, 200, 3)))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(10, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Flatten())
model.add(layers.Dense(10, activation='relu'))
model.add(layers.Dense(4, activation='softmax'))


optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)
model.compile(optimizer=optimizer,
              loss='categorical_crossentropy',
              metrics=['accuracy'])

history = model.fit(
    train_data_augmented,
    steps_per_epoch=len(train_images) // 64,  
    epochs=10,
    validation_data=val_data_augmented
)

# plot the accuracy and loss

def plot_and_save_curves(history, filename="curves.png"):
    """
    Plots and saves separate loss and accuracy curves for training and validation metrics.
    """
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    accuracy = history.history['accuracy']
    val_accuracy = history.history['val_accuracy']

    epochs = range(len(history.history['loss']))

    # Plot loss and accuracy on the same figure
    
    # Plot loss
    plt.plot(epochs, loss, label='training_loss')
    plt.plot(epochs, val_loss, label='val_loss')
    plt.title('Loss')
    plt.xlabel('Epochs')
    plt.legend()
    
    plt.savefig(filename.replace(".png", "_loss.png"))
    plt.close()

    # Plot accuracy
    plt.figure()
    plt.plot(epochs, accuracy, label='training_accuracy')
    plt.plot(epochs, val_accuracy, label='val_accuracy')
    plt.title('Accuracy')
    plt.xlabel('Epochs')
    plt.legend();
    
    # Save the figure
    plt.savefig(filename.replace(".png", "_accuracy.png"))
    plt.close()

plot_and_save_curves(history, filename="curves.png")


















