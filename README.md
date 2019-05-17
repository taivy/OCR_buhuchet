Получить массив Numpy из картинки можно с помощью загрузки через cv2:
img = cv2.imread(imgfile)
Либо через загрузив в io.BytesIO() объект класса Image из библиотеки PIL (Pillow):
imgByteArr = io.BytesIO()
image.save(imgByteArr, format='PNG')
resp = get_yandex_cloud_ocr_response(imgByteArr.getvalue())

#Модуль ocr_funcs
ocr_buhuchet(image)
Принимает на вход картинку (страницу) и возвращает распознанные коды с датами
Картинка должна быть в формате массива Numpy

#Модуль crop
crop_frames(image)
Принимает на вход картинку (объект класса Image из библиотеки PIL (Pillow)) и обрезает пустые края страницы (нужно, чтобы яндекс лучше распознавал)

#Модуль yandex_ocr_request
get_yandex_cloud_ocr_response(image_data)
Принимает на вход картинку (страницу) и возвращает ответ от яндекса с распознанным текстом и координатами
Картинка должна быть в формате массива Numpy
