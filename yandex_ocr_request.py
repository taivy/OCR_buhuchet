import subprocess
import base64
import requests

imgfile = 'test_buhu.jpg'
folderId = 'b1gjtg5ljkjdb3lmjv1t'

'''
with open(imgfile, 'rb') as img:
    image_data = img.read()
'''

def get_yandex_cloud_ocr_response(image_data, folderId=folderId):
    image_64_encode = base64.urlsafe_b64encode(image_data)
    image_64_encode = image_64_encode.decode('utf-8')
    
    try:
        IAM_TOKEN = subprocess.check_output(["yc", "iam", "create-token"]).decode("utf-8").strip('\n')
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
    json_request = {
            "Authorization": "Bearer %s" % IAM_TOKEN,
            "folderId": folderId,
            "analyze_specs": [{
                "content": image_64_encode,
                "features": [{
                    "type": "TEXT_DETECTION",
                    "text_detection_config": {
                        "language_codes": ["en", "ru"]
                }
            }]
        }]
    }
    
    headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % IAM_TOKEN
            }
    
    url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'

    resp = requests.post(url, headers=headers, json=json_request)
        
    return resp.text
