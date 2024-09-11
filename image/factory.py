"""
image factory
"""


def create_image(image_type):
    """
    create a image instance
    :param image_type: image type code
    :return: image instance
    """
    if image_type == "openai":
        from image.openai.openai_image import OpenaiImage

        return OpenaiImage()
    raise RuntimeError
