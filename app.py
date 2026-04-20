from flask import Flask, render_template, request, jsonify
import requests
import xmltodict
from datetime import datetime

app = Flask(__name__)

# 공공데이터 API 설정
API_URL = 'http://apis.data.go.kr/B552657/ErmctInsttInfoInqireService/getParmacyListInfoInqire'
SERVICE_KEY = '1a5c480046f5f7743dd14af612dfe3124661fd0307929f4ce7043f0d7dc55961' # 여기에 인증키 입력

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/pharmacies')
def get_pharmacies():
    city = request.args.get('city', '부산광역시')
    district = request.args.get('district', '수영구')
    
    params = {
        'serviceKey': SERVICE_KEY,
        'Q0': city,
        'Q1': district,
        'numOfRows': 100
    }

    try:
        response = requests.get(API_URL, params=params)
        dict_data = xmltodict.parse(response.content)
        items = dict_data['response']['body']['items']
        
        if not items:
            return jsonify([])

        item_list = items['item']
        if isinstance(item_list, dict): # 결과가 1개일 경우 처리
            item_list = [item_list]

        now = datetime.now()
        weekday = now.isoweekday() # 1:월, ..., 7:일
        current_time = int(now.strftime('%H%M'))

        opened = []
        for item in item_list:
            start_key = f'dutyTime{weekday}s'
            end_key = f'dutyTime{weekday}e'

            if start_key in item and end_key in item:
                if int(item[start_key]) <= current_time <= int(item[end_key]):
                    opened.append({
                        'name': item['dutyName'],
                        'address': item['dutyAddr'],
                        'tel': item['dutyTel1'],
                        'endTime': item[end_key]
                    })
        return jsonify(opened)
    except:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
