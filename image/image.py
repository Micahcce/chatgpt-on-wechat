"""
Image service abstract class
"""
import base64

class Image(object):
    def imageRecg(self, image_path):
        """
        Send image recognition service and get image recognition result
        """
        raise NotImplementedError

    def imageCreate(self, text):
        """
        Send image create service and get image create result
        """
        raise NotImplementedError
    
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')