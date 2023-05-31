import unittest
import base64
import app

class app_test(unittest.TestCase):
    # Setting up the app_test class.
    def setUp(self):
        '''
        Opening a correct image that includes a face.
        Encoding it into b64 just like the browser would.
        '''
        with open('./test/test_img_f.jpg', "rb") as image:
            self.test_im = image.read()
            self.test_im = bytearray(self.test_im)
            self.test_im = base64.b64encode(self.test_im)
            self.test_im = "data:image/png;base64," + str(self.test_im)
            self.test_im = self.test_im.replace("b'", "")
        '''
        Opening a blank image.
        Encoding it into b64 just like the browser would.
        '''
        with open('./test/blankImage.png', "rb") as image:
            self.test_im_blank = image.read()
            self.test_im_blank = bytearray(self.test_im_blank)
            self.test_im_blank = base64.b64encode(self.test_im_blank)
            self.test_im_blank = "data:image/png;base64," + str(self.test_im_blank)
            self.test_im_blank = self.test_im_blank.replace("b'", "")

        app.app.testing = True
        self.app = app.app.test_client()

    '''
    Testing the landing page.
    1. Should connect with a statuc code of 200
    2. HTML must contain elements from index.html
    '''
    def test_home(self):
        result = self.app.get('/')
        html = result.data.decode()
        assert result.status_code == 200
        assert '<h1>Let the machine guess your age and gender</h1>' in html
        assert '<div id="webcam_with_polaroid">' in html
    
    '''
     Testing the bounding boxes with a correct image.
     1. Detection must be a success, returns True
     2. Return a dict with 5 key/value pairs.
     3. The values that build the bounding box are integers.
    '''
    def test_bbox_with_correct_image(self):
        result = self.app.post('/images', data=dict(method='POST', image=self.test_im))    
        result_json = result.get_json()
        self.assertTrue(result_json.get('detection'))
        self.assertEqual(len(result_json), 5)
        self.assertIsInstance(result_json.get('x'), int)
        self.assertIsInstance(result_json.get('y'), int)
        self.assertIsInstance(result_json.get('w'), int)
        self.assertIsInstance(result_json.get('h'), int)
    
    '''
    Testing the bounding boxes with a correct image.
    1. Detection must fail, returns False.
    2. Return a dict with 1 key/value pair, "detection"
    '''
    def test_bbox_with_blank_image(self):
        result = self.app.post('/images', data=dict(method='POST', image=self.test_im_blank))    
        result_json = result.get_json()
        self.assertFalse(result_json.get('detection'))
        self.assertEqual(len(result_json), 1)

    '''
    Testing the classifier with a correct image.
    1. Detection must be a success, returns True
    2. The length of the result should be 3, includes "detection", "gender" and "age"
    3. Gender variable is a string and age variable is also a string
    '''
    def test_classification_with_correct_image(self):
        result = self.app.post('/classify', data=dict(method='POST', image=self.test_im))    
        result_json = result.get_json()
        self.assertTrue(result_json.get('detection'))
        self.assertEqual(len(result_json), 3)
        self.assertIsInstance(result_json.get('gender'), str)
        self.assertIsInstance(result_json.get('age'), str)

    '''
    Testing the classifier with a blank image.
    1. Detection must fail, returns False
    2. The length of the result should be 1, includes only "detection"
    '''
    def test_classification_with_blank_image(self):
        result = self.app.post('/classify', data=dict(method='POST', image=self.test_im_blank))    
        result_json = result.get_json()
        self.assertFalse(result_json.get('detection'))
        self.assertEqual(len(result_json), 1)

if __name__ == "__main__":
    unittest.main()