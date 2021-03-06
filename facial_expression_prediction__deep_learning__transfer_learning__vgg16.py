# -*- coding: utf-8 -*-
"""Facial Expression Prediction_ Deep Learning _Transfer Learning _VGG16.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rpt6J-EGXQrkLNADFbMAOeM8-h7CRVf_
"""

! pip install tensorflow-gpu

! pip install keras

! pip install pandas

import matplotlib.pylab as plt
import numpy as np
import tensorflow_hub as hub
import tensorflow as tf
print("TF version:", tf.__version__)
print("Hub version:", hub.__version__)
print("GPU is", "available" if tf.test.is_gpu_available() else "NOT AVAILABLE")

from tensorflow.keras.layers import Input, Lambda, Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.applications.resnet50 import ResNet50
#from tensorflow.keras.applications.resnet152V2 import ResNet152V2
from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator,load_img
from tensorflow.keras.models import Sequential
from glob import glob
from keras.applications.inception_v3 import InceptionV3
#from keras.applications.inception_v3 import preprocess_input, decode_predictions

from sklearn.utils import shuffle
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix,accuracy_score
import os
import cv2

from google.colab import drive
drive.mount('/content/drive')

X = []
y = []
IMG_SIZE = 224
DIR = "/content/drive/My Drive/Colab Notebooks/Facial Expressions"
folders1 = os.listdir(DIR)
folders1

for i, file in enumerate(folders1):
    filename = os.path.join(DIR, file)
    print("Folder {} started".format(file))
    try:
        for img in os.listdir(filename):
            path = os.path.join(filename, img)
            img = cv2.imread(path,cv2.IMREAD_COLOR)
            img = cv2.resize(img, (IMG_SIZE,IMG_SIZE))

            X.append(np.array(img))
            y.append(i)
    except:
        print("File {} not read".format(path))
        
    print("Folder {} done".format(file))
    print("The folder {} is labeled as {}".format(file, i))

print(len(X))
print(len(y))

import random
from random import sample
plt.figure(figsize=(10,10))
random_indexes = sample(range(1, 982), 16)
print(random_indexes)
for i, img_index in enumerate(random_indexes):

  # Set up subplot; subplot indices start at 1
  sp = plt.subplot(8,2, i + 1)
  sp.set_title(folders1[y[img_index]])
  sp.axis('Off') # Don't show axes (or gridlines)
  plt.imshow(X[img_index])

X = np.array(X)
y = np.array(y)

print("X shape is {}".format(X.shape))
print("y shape is {}".format(y.shape))

from tensorflow.keras.utils import to_categorical

print("Before the categorical the shape of y is {}".format(y.shape))
y = to_categorical(y)
print("After the categorical the shape of y is {}".format(y.shape))

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=10)

print("There are {} training examples".format(X_train.shape[0]))
print("There are {} test examples".format(X_test.shape[0]))

training_datagen = ImageDataGenerator(
      rescale = 1./255,
      rotation_range=40,
      width_shift_range=0.2,
      height_shift_range=0.2,
      shear_range=0.2,
      zoom_range=0.2,
      horizontal_flip=True,
      fill_mode='nearest',
      cval=5)


validation_datagen = ImageDataGenerator(
      rescale = 1./255)

training_set=training_datagen.flow(X_train,y_train)
test_set=validation_datagen.flow(X_test,y_test)

IMAGE_SIZE=[224,224]
vgg= VGG16(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)

  # don't train existing weights\n",
for layer in vgg.layers:
  layer.trainable = False

folders = glob('/content/drive/My Drive/Colab Notebooks/Facial Expressions/*')
x = Flatten()(vgg.output)
prediction=Dense(len(folders), activation='softmax')(x)
model = Model(inputs=vgg.input, outputs=prediction)
model.summary()

model.compile(
  loss='categorical_crossentropy',
  optimizer='adam',
  metrics='accuracy')
batch_size=32
  
r= model.fit_generator(training_set,epochs = 25, validation_data = test_set,verbose = 1, steps_per_epoch=X_train.shape[0] // batch_size, validation_steps=X_test.shape[0] // batch_size)

  # plot the loss
plt.figure(figsize=(10,6))

plt.subplot(1,2,1)
plt.plot(r.history['loss'], label='train loss')
plt.plot(r.history['val_loss'], label='val loss')
plt.legend()
plt.savefig('LossVal_loss')

  # plot the accuracy
plt.subplot(1,2,2)
plt.plot(r.history['accuracy'], label='train acc')
plt.plot(r.history['val_accuracy'], label='val acc')
plt.legend()
plt.savefig('AccVal_acc')

print('The Validation Accuracy of VGG16: ', np.mean(r.history['val_accuracy']))

print('The Validation Accuracy of VGG19: ', np.mean(r.history['val_accuracy']))

# save it as a h5 file
from tensorflow.keras.models import load_model
model.save('Facial_model_VGG16.h5')

y_pred = model.predict(X_test)
y_pred_digits = np.argmax(y_pred, axis=1)
y_pred_digits

y_pred_labels = np.unique(y_pred_digits, return_counts=True)
y_pred_labels

real_labels= np.argmax(y_test, axis=1)
real_labels
real_labels1 = np.unique(real_labels, return_counts=True)
real_labels1

from sklearn.metrics import confusion_matrix
c_m = confusion_matrix(real_labels, y_pred_digits)
c_m

import seaborn as sns
plt.figure(figsize = (6,6))
sns.heatmap(c_m,cmap= "Reds", linecolor = 'black' , linewidth = 1 , annot = True, fmt='' , xticklabels = folders1 , yticklabels = folders1)
plt.xlabel('Predited')
plt.ylabel('Actual')
plt.show()

from sklearn.metrics import confusion_matrix,roc_curve,auc,accuracy_score
acc_score = accuracy_score(real_labels, y_pred_digits)
acc_score

# now storing some properly as well as misclassified indexes'.
i=0
prop_class=[]
mis_class=[]

for i in range(len(real_labels)):
    if(real_labels[i] == y_pred_digits[i]):
        prop_class.append(i)
    if(len(prop_class)==10):
        break
i=0
for i in range(len(real_labels)):
    if(real_labels[i] != y_pred_digits[i]):
        mis_class.append(i)

print(len(prop_class))
print(len(mis_class))

labels_names={0:'Contempt', 
        1:'Disgust',
        2:'Surprise',
        3:'Fear',
        4:'Sadness',
        5:'Anger',
        6:'Happy'
        }
#fig.set_size_inches(8,8)
import random
from random import sample
plt.figure(figsize=(18,18))
random_indexes = sample(range(0, 10), 10)
print(random_indexes)
for i, img_index in enumerate(random_indexes):

  # Set up subplot; subplot indices start at 1
  sp = plt.subplot(5, 2, i + 1)
  sp.set_title('Actual Expression: '+ labels_names[real_labels[prop_class[img_index]]]+ '\n' + 'Predicted Expression : ' + labels_names[y_pred_digits[prop_class[img_index]]])
  sp.axis('Off') # Don't show axes (or gridlines)
  plt.imshow(X_test[prop_class[img_index]])

labels_names={0:'Contempt', 
        1:'Disgust',
        2:'Surprise',
        3:'Fear',
        4:'Sadness',
        5:'Anger',
        6:'Happy'
        }
import random
from random import sample

random_indexes = sample(range(0, 10), 10)
print(random_indexes)
plt.figure(figsize=(25,25))
for i, img_index in enumerate(random_indexes):
  # Set up subplot; subplot indices start at 1
  sp = plt.subplot(5, 2, i + 1)
  sp.set_title('Actual Bird: '+ labels_names[real_labels[mis_class[img_index]]]+ '\n' + 'Predicted Bird : ' + labels_names[y_pred_digits[mis_class[img_index]]])
  sp.axis('Off') # Don't show axes (or gridlines)
  plt.imshow(X_test[mis_class[img_index]])

# Evaluate The Model with Different Images

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

model=load_model('Facial_model_VGG16.h5')

img=image.load_img('/content/drive/My Drive/Colab Notebooks/brahman/angry.jpeg',target_size=(224,224))

img

y=image.img_to_array(img)
y=np.expand_dims(y,axis=0)
imgy=preprocess_input(y)
imgy=imgy/255

preds= model.predict(imgy)
preds

a=np.argmax(preds, axis=1)
a

if(a==0):
    print("Contempt")
elif(a==1):
    print("Disgust")
elif(a==2):
    print("Surprise")
elif(a==3):
    print("Fear")
elif(a==4):
    print("Sadness")
elif(a==5):
    print("Anger")
else:
  print("Happy")



