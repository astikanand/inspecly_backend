import cv2

def np_array_to_byte_image(np_array):
    _, byte_image = cv2.imencode('.png', np_array)
    byte_image = byte_image.tobytes()

    return byte_image


class CV2Colors:
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (0, 255, 255)
    CYAN = (255, 255, 0)
    MAGENTA = (255, 0, 255)
    GRAY = (128, 128, 128)
    ORANGE = (0, 165, 255)
    PINK = (203, 192, 255)
    PURPLE = (128, 0, 128)
    BROWN = (42, 42, 165)


