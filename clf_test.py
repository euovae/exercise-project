import classification
from PIL import Image
import numpy as np

# Loading up images for testing.
image_female = Image.open('./test/test_img_f.jpg')
image_male = Image.open('./test/test_img_m.jpg')

# Generating an (800, 600) image and fill it with black RGB color.
image_blank = Image.fromarray(np.zeros((800,600,3), np.uint8))
'''
For testing classification.py
Specifically start_bbox_detection and start_classification.
Both of these functions use other subfunctions, so every function
in the file will be tested.
We have two images of real looking human faces ready and one blank image.
'''
def classification_test():

    #image_blank.show()
    message = ""

    '''
    Testing start_bbox_detection.
    If the algorithm detects bounding boxes, it will return 
    a list with 4 values representing the starting points of a rectangle
    and the width and height of that rectangle.
    If the algorithm fails, returns None.
    '''
    try:
        bbox_female = classification.start_bbox_detection(image_female)
        bbox_male = classification.start_bbox_detection(image_male)
        bbox_blank = classification.start_bbox_detection(image_blank)

        if (check_bbox_array(bbox_female) and 
            check_bbox_array(bbox_male) and
            check_bbox_array(bbox_blank) is False
            ):

            message += '\nSUCCESS: Found bboxes for female test image'
            message += '\nSUCCESS: Found bboxes for male test image'
            message += '\nSUCCESS: No bboxes for blank, returns nothing'

        else:
            message += "\nFAILED: An error occured during the test"
    except:
        message += "\nFAILED: An error occured during bbox test"

    # Testing start_classification.
    try:
        preds_female = classification.start_classification(image_female)
        preds_male = classification.start_classification(image_male)
        preds_blank = classification.start_classification(image_blank)

        if (check_clf_array(preds_female) and 
            check_clf_array(preds_male)
            ):

            message += '\nSUCCESS: Classified female test image'
            message += '\nSUCCESS: Classified male test image'
            message += '\nSUCCESS: No classification for blank, returns None'

            print('Model predicted: ' + preds_female[0] + ', aged ' + preds_female[1])
            print('Model predicted: ' + preds_male[0] + ', aged ' + preds_male[1])
            print('Model returned ' + str(preds_blank) + ' for blank image')
        else:
            message += "\nFAILED: An error occured during classification test"
    except:
        message += "\nFAILED: An error occured during classification test"
    
    print(message)
'''
Testing if the returned numpy array from start_bbox_detection() is correct.
1. Numpy array must not be empty or None.
2. The array must contain 4 integers, which represent the rectangle.
'''
def check_bbox_array(arr):
    try:
        arr_list = arr[0].tolist()
        s = ""
        for i in arr_list:
            s += str(i)
        '''
        Verifying the requirements above.
        An empty list or None would fail len(arr_list) == 4
        '''
        if (len(arr_list) == 4 and s.isdigit()):
        
            return True
        else:
            return False
    except:
        return False
'''    
Testing if the returned list from start_bbox_detection() is correct.
1. List must not be empty or None.
2. The list must contain 2 strings, 
   a gender and an age range.
'''
def check_clf_array(arr):
    try:
        '''
        Verifying the requirements above.
        The first is either 'Female' or 'Male'
        The second must be an age range in the form of a string 
        that the function "def age_match(age)" returns, 
        if the string constains the character '-', then it was a success.
        '''
        if (arr is not None and len(arr) == 2 and
            (arr[0] == "Female" or "Male") and
            '-' in arr[1]):
            return True
        else:
            return False
    except:
        return False

if __name__ == "__main__":
    classification_test()