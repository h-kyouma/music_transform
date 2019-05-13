import cv2

def save_img(name, image):
    cv2.imwrite(name, image)
    
def load_image(name):
    return cv2.imread(name, -1)
