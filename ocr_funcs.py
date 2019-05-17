import json
from itertools import chain
from collections import namedtuple
import re
#import numpy as np
#from PIL import ImageFont, ImageDraw, Image


months_dict = {
    "январ": '01',
    "феврал": "02",
    "март": "03",
    "апрел": "04",
    "май": "05",
    "мая": "05",
    "июн": "06",
    "июл": "07",
    "август": "08",
    "сентябр": "09",
    "октябр": "10",
    "ноябр": "11",
    "декабр": "12"   
}



def ocr_buhuchet(data, debug_mode=False):
    data = json.loads(data)
        
    x_1 = None
    
    code = None    
    codes_y = []    
    codes_nums = dict()
    
    for page in data['results'][0]['results'][0]['textDetection']['pages']:
        for smth in page['blocks']:
            for line in smth['lines']:
                line_bb = line['boundingBox']['vertices']
                line_string = ''.join([word['text'] for word in line['words']])
                #cv2.putText(img,line_string, (int(line_bb[0]['x']), int(line_bb[0]['y'])), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,0,255))

                if 'код' in line_string.lower():
                    x_1 = int(line_bb[0]['x'])
                    #x_2 = int(line_bb[2]['x'])
                    code_y_1 = int(line_bb[0]['y'])
                    code_y_2 = int(line_bb[2]['y'])
                    #draw.rectangle(((int(line_bb[0]['x']), code_y_1), (int(line_bb[2]['x']), code_y_2)), fill=(0,255,255))
                    dates_max_threshold = 5*(code_y_2 - code_y_1)
                    break
    
    date_cell = ''
    dates = []
    first_cell = True
    date_cell_threshold = 90
    dates_x = []
    
    for page in data['results'][0]['results'][0]['textDetection']['pages']:
        for smth in page['blocks']:
            for line in smth['lines']:
                line_bb = line['boundingBox']['vertices']
                line_string = ''.join([word['text'] for word in line['words']])
                #if abs(x_1 - int(line_bb[0]['x'])) < threshold and abs(x_2 - int(line_bb[2]['x'])) < threshold:
                if abs(x_1 - int(line_bb[0]['x'])) < 80:
                    try:
                        if re.search('[А-Яа-я]', line_string) is not None:
                            continue
                        int(line_string)
                        code = line_string
                    except:
                        # check if not code
                        try:
                            code = line_string.split(' ')[0]
                            code = code.split('(')[0]
                            int(code)
                        except:
                            continue
                    code_y = dict()
                    code_y['name'] = code
                    y_1 = int(line_bb[0]['y'])
                    y_2 = int(line_bb[2]['y'])
                    code_y['y_1'] = y_1
                    code_y['y_2'] = y_2
                    codes_nums[code] = []
                    codes_y.append(code_y)
                elif abs(code_y_1 - int(line_bb[0]['y'])) < dates_max_threshold and abs(code_y_2 - int(line_bb[2]['y'])) < dates_max_threshold:
                    if x_1 > int(line_bb[0]['x']):
                        continue
                    if first_cell:
                        #prev_x = int(line_bb[0]['x'])
                        date_cell_threshold = 1.2*(int(line_bb[0]['x']) - x_1)
                        first_cell = False
                    for date_string_dict in dates_x:
                        date_x = date_string_dict['x']
                        if abs(date_x - int(line_bb[0]['x'])) < date_cell_threshold:
                            date_string_dict['content'] += ' ' + line_string
                            continue
                    else:
                        date_string_dict = dict()
                        date_string_dict['x'] = int(line_bb[0]['x'])
                        date_string_dict['content'] = line_string
                        dates_x.append(date_string_dict)
    
    dates_x.append(date_string_dict) # append last
    dates_new_x = []
    months_re = '(январ|феврал|март|апрел|май|мая|июн|июл|август|сентябр|октябр|ноябр|декабр)'
    date_string_to_parse_tuple = namedtuple('date_string_to_parse', 'content datestr_type')
    datestr_type_date_pattern = re.compile('(\d{1,2})\s*' + months_re + '\w*\s*([\d]{4})')
    datestr_type_months_pattern = re.compile(months_re + '([А-Яа-я\-]*\s*)*' + months_re + '[А-Яа-я\-]*\s*([\d]{4})')
    #print('DATES ', dates_x)
    for date_str_dict in dates_x:
        try:
            if datestr_type_date_pattern.search(date_str_dict['content']) is not None:
                date_string_to_parse = date_string_to_parse_tuple(date_str_dict['content'], 'date')
                dates_new_x.append(date_string_to_parse)
            elif datestr_type_months_pattern.search(date_str_dict['content']) is not None:
                date_string_to_parse = date_string_to_parse_tuple(date_str_dict['content'], 'months')
                dates_new_x.append(date_string_to_parse)
        except Exception as e:
            print(e)
            continue
    
    dates.append(date_cell) # append last
    dates_formatted = []
    
    for date_string_to_parse in dates_new_x:
        if date_string_to_parse.datestr_type == 'date':
            date_string_parsed = datestr_type_date_pattern.search(date_string_to_parse.content)
            day = date_string_parsed.group(1)
            month = months_dict[date_string_parsed.group(2)]
            year = date_string_parsed.group(3)
            date = day + '.' + month + '.' + year
        if date_string_to_parse.datestr_type == 'months':
            date_string_parsed = datestr_type_months_pattern.search(date_string_to_parse.content)
            month1 = months_dict[date_string_parsed.group(1)]
            month2 = months_dict[date_string_parsed.group(3)]
            year = date_string_parsed.group(4)
            date = month1 + '-' + month2 + '.' + year
        if date not in dates_formatted:
            dates_formatted.append(date)
    #print('DATES PARSED', dates_formatted)
    
    # sort lines and find nums
    for page in data['results'][0]['results'][0]['textDetection']['pages']:
        blocks = list(chain(page['blocks']))
        lines = []
        for block in blocks:
            for line in block['lines']:
                lines.append(line)
        offset = 0.1
        lines.sort(key = lambda line: (round(int(line['words'][0]['boundingBox']['vertices'][0]['y'])//2*offset), int(line['words'][0]['boundingBox']['vertices'][0]['x'])))
        for line in lines:
            line_bb = line['boundingBox']['vertices']
            line_string = ''.join([word['text'] for word in line['words']])
            threshold = 2*(code_y_2 - code_y_1)
            for code in codes_y:
                y_1 = code['y_1']
                y_2 = code['y_2']
                if abs(y_1 - int(line_bb[0]['y'])) < threshold and abs(y_2 - int(line_bb[2]['y'])) < threshold:
                    '''
                    try:
                        num = int(line_string)
                    except ValueError:
                        continue
                    '''
                    num = line_string
                    if str(num) != code['name']:
                        try:
                            num = re.search('\(*([0-9]+)\)*', num).group(0)
                        except:
                            continue
                        codes_nums[code['name']].append(num)
                        
    codes_dates_dict = dict()
    
    for code, values in codes_nums.items():
        codes_dates_dict[code] = dict()
        for ind, value in enumerate(values):
            try:
                codes_dates_dict[code][dates_formatted[ind]] = value
            except:
                #print('Index error: ', code, ind, value)
                pass
    return codes_dates_dict


#print(ocr_buhuchet(data, debug_mode=True))