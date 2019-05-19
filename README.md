# Получение массива NumPy из картинки
Получить массив Numpy из картинки можно с помощью загрузки через cv2:

```img = cv2.imread(imgfile)```

Либо через загрузив в io.BytesIO() объект класса Image из библиотеки PIL (Pillow):

```
import io
imgByteArr = io.BytesIO()
image.save(imgByteArr, format='PNG')
resp = get_yandex_cloud_ocr_response(imgByteArr.getvalue())
```

# Получение результата для pdf файлов
Получить объекты Image из страниц с помощью функции convert_from_bytes из библиотеки pdf2image, получить и объединить результаты

```
from itertools import chain
from pdf2image import convert_from_bytes
from crop import crop_frames
from yandex_ocr_request_func import get_yandex_cloud_ocr_response
from ocr_funcs import ocr_buhuchet

pages = convert_from_bytes(f.read())
result = []
for page in pages:
    cropped_page = crop_frames(page, i=i)
    imgByteArr = io.BytesIO()
    cropped_page.save(imgByteArr, format='PNG')
    resp = get_yandex_cloud_ocr_response(imgByteArr.getvalue())
    r = ocr_buhuchet(resp, debug_mode=False)
    result = list(chain(result, [r]))
```

# Модуль ocr_funcs
ocr_buhuchet(image)

Принимает на вход картинку (страницу) и возвращает распознанные коды с датами

Картинка должна быть в формате массива Numpy

# Модуль crop
crop_frames(image)

Принимает на вход картинку (объект класса Image из библиотеки PIL (Pillow)) и обрезает пустые края страницы (нужно, чтобы яндекс лучше распознавал)

# Модуль yandex_ocr_request
get_yandex_cloud_ocr_response(image_data)

Принимает на вход картинку (страницу) и возвращает ответ от яндекса с распознанным текстом и координатами

Картинка должна быть в формате массива Numpy
