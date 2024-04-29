from tensorflow.keras.models import load_model
import numpy as np
from tensorflow.keras.applications.inception_resnet_v2 import preprocess_input
from PIL import Image
from io import BytesIO
import pytesseract
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

model = load_model('/Users/kamyar/University/Computer Project '
                   '/Webapp/Webapp/AI_models/best_weights_InceptionResnetV3_multiclass_3.hdf5')
class_names = ['Analytical', 'EM', 'Not_Related']
Raman_FTIR = ['wavenumber', 'raman', 'shift', 'wave numbers', 'wave number']
DLS = ['size', 'particle size', '(nm)', 'particle diameter']
UV_Vis = ['wavelength', 'absorption', 'wave length', 'wavelength(nm)', 'λ(nm)']
XRD = [' 2θ ', ' θ ', 'degree', 'theta', 'deg', '(°)', '(° )']
EDSXPS = ['kev', 'energy', 'binding', 'kinetic', '(ev)']
custom_config_1 = r'--oem 3 --psm 11 -l eng'
custom_config_2 = r'--oem 3 --psm 11 -l eng+grc'
custom_config_3 = r'--oem 3 --psm 11 -l grc -c tessedit_char_whitelist=2θλ'


def preprocess_image(image):
    image = image.resize((299, 299))
    image = np.array(image)
    image = preprocess_input(image)
    if image.shape[-1] > 3:
        image = image[:, :, :3]
    return image


def predict_from_url(image_content):
    # response = requests.get(image_url)
    image = Image.open(BytesIO(image_content))
    preprocessed_image = preprocess_image(image)
    preprocessed_image = np.expand_dims(preprocessed_image, axis=0)
    predictions = model.predict(preprocessed_image)
    predicted_classes = np.argmax(predictions, axis=1)
    class_name = class_names[predicted_classes[0]]
    # if class_name == 'Analytical':
    #     class_name = predict_analytical_class(image)
    return class_name


def predict_analytical_class(preprocessed_image):
    class_name = []
    flag = 0
    grc_model = pytesseract.image_to_string(preprocessed_image, config=custom_config_3).lower()
    eng_model = pytesseract.image_to_string(preprocessed_image, config=custom_config_1).lower()
    mixed_language_model = pytesseract.image_to_string(preprocessed_image, config=custom_config_2).lower()

    if (Raman_FTIR[0] in eng_model) or (Raman_FTIR[1] in eng_model) or (Raman_FTIR[2] in eng_model) or (
            Raman_FTIR[3] in eng_model) or (Raman_FTIR[4] in eng_model):
        class_name.append('Raman')
        flag = 1

    if (UV_Vis[0] in eng_model) or (UV_Vis[1] in eng_model) or (UV_Vis[2] in eng_model) or (UV_Vis[3] in eng_model) or (
            UV_Vis[4] in mixed_language_model):
        class_name.append('UV-Vis')
        flag = 1

    if (XRD[0] in grc_model) or (XRD[1] in grc_model) or (XRD[2] in eng_model) or (XRD[3] in eng_model) or (
            XRD[4] in eng_model) or (XRD[5] in eng_model) or (XRD[6] in eng_model):
        class_name.append('XRD')
        flag = 1

    if flag == 0:
        class_name = 'Others'

    return class_name

# if __name__ == '__main__':
# test = predict_from_url('https://www.mdpi.com/nanomaterials/nanomaterials-11-02377/article_deploy/html/images/nanomaterials-11-02377-g001.png')
# print(test)
# chrome_options = Options()
# chrome_options.add_argument("--incognito")
# chrome_options.add_argument("--window-size=1920x1080")
# driver = webdriver.Chrome(options=chrome_options)
# driver.get(
#     'https://www.tandfonline.com/cms/asset/ad30ec8f-984c-4041-8360-cc0a173680dc/tgcl_a_2018506_f0003_oc.jpg')
# image_content = driver.find_element(By.TAG_NAME, 'img').screenshot_as_png
# print(predict_from_url(image_content))
