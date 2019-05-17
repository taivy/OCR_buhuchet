from flask import Flask, render_template, request
from pdf2image import convert_from_bytes
import io
from itertools import chain

from yandex_ocr_request_func import get_yandex_cloud_ocr_response
from ocr_funcs import ocr_buhuchet
from crop import crop_frames


ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'bmp'])

app = Flask(__name__)



@app.route('/')
def main():
    return render_template('index.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f.mimetype.endswith('pdf'):
            pages = convert_from_bytes(f.read())
            result = []
            i = 0
            for page in pages:
                cropped_page = crop_frames(page, i=i)
                imgByteArr = io.BytesIO()
                cropped_page.save(imgByteArr, format='PNG')
                resp = get_yandex_cloud_ocr_response(imgByteArr.getvalue())
                r = ocr_buhuchet(resp, debug_mode=False)
                result = list(chain(result, [r]))
                i+=1                
        else:
            image_data = f.read()
        
            resp = get_yandex_cloud_ocr_response(image_data)
            r = ocr_buhuchet(resp)
            result = r
        return render_template('recognized.html', result=result)
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
