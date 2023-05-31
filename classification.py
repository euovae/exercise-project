import cv2 as cv
import numpy as np
import tensorflow as tf

# Loading up the cascadeclassifier for detecting the bounding boxes of faces.
face_cc = cv.CascadeClassifier('./static/haarcascade_frontalface_default.xml')

# Loading and compiling tensorflow/keras models
gender_model = tf.keras.models.load_model('gender_model_2', compile=True)
age_model = tf.keras.models.load_model('age_model', compile=True)

# Function for starting up the classification process
def start_classification(im):
    return classify_face(detect_and_crop(*pil_to_opencv(im, True)))

# Function for starting up the face detection process
def start_bbox_detection(im):
    return detect_bbox(pil_to_opencv(im, False), False)

# Converting pil to opencv
def pil_to_opencv(pil_im, return_min_dim):
    #print(pil_im.format)
    #print(pil_im.size)
    #print(pil_im.mode)
    min_dim = min(pil_im.size)
    img = cv.cvtColor(np.asarray(pil_im), cv.COLOR_RGB2BGR)
    return (img, min_dim) if return_min_dim else img

# Preprocessing the images to have the exact same shape as the training examples.
def preprocess_image(image):
    img_width = img_height = 48
    return np.reshape(image,(1,)+(img_width, img_height) + (1,))

def classify_face(image):
    if image is None:
        return None
    else:
        #cv.imwrite('image', image)
        # Converting a numpy array to tensor. Not needed.
        prepped_image = tf.convert_to_tensor(preprocess_image(np.array(image)))
        
        # Predictions
        pred_gender = gender_model.predict(prepped_image, verbose = 0)
        pred_age = age_model.predict(prepped_image, verbose = 0)
        print(pred_gender)
        
        # Returning the class with the highest probability.
        return [gender_match(np.argmax(pred_gender)), age_match(np.argmax(pred_age))]

def detect_bbox(image, return_gray):
    
    # Converting image to grayscale
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # Detecting the bounding boxes, using the cascade classifier.
    faces_bbox = face_cc.detectMultiScale(image_gray, scaleFactor=1.05, minNeighbors=6, minSize=[48,48])
    
    return (faces_bbox, image_gray) if return_gray else faces_bbox

# Drawing the bounding boxes and cropping the image.
def detect_and_crop(im, min_dim):
    # Resizing the images into a square, which resulted in better accuracy.
    image = cv.resize(im, (min_dim, min_dim), interpolation = cv.INTER_AREA)
    # Obtaining the bounding boxes
    faces_bbox, image_gray = detect_bbox(image, True)
    
    # Drawing 
    for (x, y, w, h) in faces_bbox:
        cv.rectangle(image, (x, y), (x+w, y+h), (255, 255, 255), thickness=1)
    try:
        # Cropping and downsampling to (48, 48)
        #cv.imwrite('image_bbox', image)
        cropped_image = image_gray[y:y+h, x:x+w]
        return (cv.resize(cropped_image, dsize=[48,48], interpolation = cv.INTER_AREA))
    except UnboundLocalError:
        return None


# Numerical to categorical 

# Python version < 3.10
def gender_match(gender):
    if (gender == 0):
        return "Male"
    elif (gender == 1):
        return "Female"
    else:
        return 0

# Python version < 3.10
def age_match(age):
    if (age == 0):
        return "0-3"
    elif (age == 1):
        return "4-8"
    elif (age == 2):
        return "9-12"
    elif (age == 3):
        return "13-17"
    elif (age == 4):
        return "18-25"
    elif (age == 5):
        return "26-35"
    elif (age == 6):
        return "36-45"
    elif (age == 7):
        return "46-55"
    elif (age == 8):
        return "56-65"
    elif (age == 9):
        return "65+"
    else:
        return 0

'''
# Python version >= 3.10
def gender_match(gender):
    match gender:
        case 0:
            return "Male"
        case 1:
            return "Female"
        case _:
            return 0

# Python version >= 3.10
def age_match(age):
    match age:
        case 0:
            return "0-3"
        case 1:
            return "4-8"
        case 2:
            return "9-12"
        case 3:
            return "13-17"
        case 4:
            return "18-25"
        case 5:
            return "26-35"
        case 6:
            return "36-45"
        case 7:
            return "46-55"
        case 8:
            return "56-65"
        case 9:
            return "65+"
        case _:
            return 0
'''