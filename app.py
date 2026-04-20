import requests
import xmltodict
from datetime import datetime

def get_opened_pharmacies(city, district):
    # 1. API 설정
    url = 'http://apis.data.go.kr/B552657/ErmctInsttInfoInqireService/getParmacyListInfoInqire'
    service_key = '자신의_디코딩_인증키_입력' # 여기에 발급받은 Decoding 인증키를 넣으세요
    
    params = {
        'serviceKey': service_key,
        'Q0': city,      # 주소(시도)
        'Q1': district,  # 주소(시군구)
        'numOfRows': 50  # 가져올 결과 수
    }

    try:
        response = requests.get(url, params=params)
        # XML 데이터를 딕셔너리로 변환
        data = xmltodict.parse(response.content)
        items = data['response']['body']['items']['item']
        
        # 현재 요일 및 시간 정보 (1:월, 2:화 ... 7:일)
        now = datetime.now()
        weekday = now.isoweekday() 
        current_time = int(now.strftime('%H%M')) # 예: 1830

        opened_list = []

        for item in items:
            # 해당 요일의 영업 시작/종료 시간 키값 생성 (예: dutyTime1s, dutyTime1e)
            start_key = f'dutyTime{weekday}s'
            end_key = f'dutyTime{weekday}e'

            if start_key in item and end_key in item:
                start_time = int(item[start_key])
                end_time = int(item[end_key])

                # 현재 시간이 영업 시간 내에 있는지 확인
                if start_time <= current_time <= end_time:
                    opened_list.append({
                        'name': item['dutyName'],
                        'address': item['dutyAddr'],
                        'tel': item['dutyTel1'],
                        'end_time': item[end_key]
                    })
        
        return opened_list

    except Exception as e:
        print(f"오류 발생: {e}")
        return []

# 실행 예시
pharmacies = get_opened_pharmacies("부산광역시", "수영구")
for p in pharmacies:
    print(f"[{p['name']}] 종료시간: {p['end_time']} | 주소: {p['address']}")
