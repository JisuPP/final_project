import datetime, json, os, pickle, requests
import pandas as pd
import numpy as np
from datetime import datetime
from konlpy.tag import Okt
from django.conf import settings
from math import radians, sin, cos, sqrt, atan2

def tokenize_user_input(user_input):
    okt = Okt()
    # 불용어 설정
    stopwords_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'ko-stopwords.csv')
    stopwords = pd.read_csv(stopwords_path)
    stopwords = list(stopwords['stopwords'])
    stopwords += [
        '에서', '고', '이다', '는', '한', '씨', '것', '거', '게', '데', '이다', '건', '고', '되다', '되어다', '걸', '기',
        '시', '네', '듯', '랍니', '중이', '얘', '스', '도도', '나', '수', '개', '내', '기', '제', '저', '인', '있다', '이렇다',
        '그렇다', '번', '위', '팅', '분', '인', '링', '란', '포', '두', '진짜', '하다', '이다', '가다', '이제', '들다',
        '너무', '먹다', '제주', '제주도', '있다', '있으며', '경우', '대부분', '조황', '로서', '조황', '있는', '최근', '그대로', '해당', '만큼', '등',
        '있게', '있으므로', '더군다나', '다시', '그', '발생', '가장', '중', '아니다', '위해',
        '후', '곳', '주로', '위해', '많다', '매일', '주로', '때문', '곳', '좋다', '좋은',
        '총', '속', '주', '후', '만', '원', '외', '등', '현재', '매장', '없다', '층', '숍', '별로', '리', '흠뻑', '의하다', '점', '도', '이러하다',
        '있는', '있었다', '비짓', '출처', '중요한', '중요하다', '특별자치도', '제주특별자치도'
    ]
    stopwords = set(stopwords)
    pos_words = okt.pos(user_input, stem=True, norm=True)

    # 형태소 분석 및 불용어 제거
    tokens = [word for word, tag in pos_words if tag in ['Noun', 'Adjective'] and word not in stopwords]
    return tokens

# matrix 불러오기
def load_tfidf_matrix(filename='tfidf_matrix.pkl'):
    file_path = os.path.join(settings.BASE_DIR,  'jeju_olleh','modules', filename)
    tfidf_mat = pd.read_pickle(file_path)
    return tfidf_mat

# vectorizer 불러오기
def load_tfidf_vectorizer(filename='tfidf_vectorizer.pkl'):
    file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', filename)
    tfidf_vect= pd.read_pickle(file_path)
    return tfidf_vect

# 두 지점 간의 Haversine 거리를 계산합니다. 
def lat_long_distance(lat1, lon1, lat2, lon2):
    
    # 지구의 반지름 (단위: km)
    R = 6371.0

    # 라디안으로 변환
    lat1 = np.radians(lat1)  # 여기서 np.radians 사용
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    
    # 위도와 경도의 차이 계산
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    # Haversine 공식 계산
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    # 거리 계산
    distance = R * c
    
    return distance

def get_address_info(address):

    # 주소를 가져오기 위한 url
    apiurl = "https://api.vworld.kr/req/address?"

    params = {
        "service": "address",
        "request": "getcoord",
        "crs": "epsg:4326",
        "address": address,
        "format": "json",
        "type": "road",
        "key": "054C4365-485B-35C4-9219-1C30E6B61D7C"
    }
    response = requests.get(apiurl, params=params)

    if response.status_code == 200:

        data = response.json()

        if 'response' in data and 'refined' in data['response'] and 'text' in data['response']['refined']:
            address = data['response']['refined']['text']
            latitude = float(data['response']['result']['point']['y'])
            longitude = float(data['response']['result']['point']['x'])
            
            # DataFrame 생성
            df = pd.DataFrame({
                'Address': [address],
                'Latitude': [latitude],
                'Longitude': [longitude]
            })

            return df
        
        else:
            print("Failed to retrieve data from the API.")
            return pd.DataFrame()  # 빈 DataFrame 반환
    else:
        print("Failed to retrieve data from the API.")
        return pd.DataFrame()  # 빈 DataFrame 반환

# 주변 날씨 정보 가져오기
def get_nearest_weather_data(place_name):
        
        # 데이터 파일 및 맵 파일 경로 설정 -> 추후에 final 파일로 변경 예정
        file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'fin_token.csv')
        map_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'map_xy.csv')

        # 데이터 파일 및 맵 파일 로딩
        df = pd.read_csv(file_path, encoding='utf-8')
        map_xy = pd.read_csv(map_path, encoding='utf-8')

        # 넘어온 명칭에 해당하는 장소의 위도, 경도값 가져오기
        target_latitude = df[df['title'] == place_name]['mapx'].round(2).values[0]
        target_longitude = df[df['title'] == place_name]['mapy'].round(2).values[0]

        # Distance 컬럼이 존재하면 삭제
        if 'Distance' in map_xy.columns:
            map_xy.drop('Distance', axis=1, inplace=True)

        # 거리 계산 후 Distance 컬럼 추가
        map_xy['Distance'] = lat_long_distance(map_xy['위도(초/100)'], map_xy['경도(초/100)'], target_latitude, target_longitude)

        # 거리순으로 정렬하여 가장 가까운 장소 정보 가져오기
        sorted_places = map_xy.sort_values(by='Distance')
        nearest_x, nearest_y = sorted_places.iloc[0][['격자 X', '격자 Y']]

        # API 키 설정
        api_key = '' 

        # 현재 날짜와 시간 설정
        base_date = datetime.now().strftime('%Y%m%d')
        
        if datetime.now().minute >= 40:
            base_time = f"{datetime.now().hour:02d}30"
        else:
            if datetime.now().hour >= 11:
                base_time = f"{datetime.now().hour - 1:02d}30"
            else:
                base_time = f"0{datetime.now().hour - 1:02d}30"

        # 날씨 데이터 가져오기
        weather_data = get_weather_data(api_key, base_date, base_time, nearest_x, nearest_y)

        # 가져온 날씨 정보를 반환
        return weather_data 

# 날씨 정보
def get_weather_data(api_key, base_date, base_time, nearest_x, nearest_y):
    
    # 초단기실황조회 url에서 정보를 가져옴
    base_url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst' 
    params = {
        'serviceKey': api_key,
        'numOfRows': '10',
        'pageNo': '1',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': nearest_x,
        'ny': nearest_y
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        try:
            data = response.json()
            weather_info_list = []

            if 'item' in data['response']['body']['items']:
                items = data['response']['body']['items']['item']
                for item in items:
                    weather_info = {}
                    category = item['category']
                    fcst_value = item['obsrValue']

                    if category == 'PTY':
                        weather_info['날씨 상태'] = get_weather_status(fcst_value)
                    elif category == 'T1H':
                        weather_info['현재 기온'] = f'{fcst_value}°C'
                    elif category == 'WSD':
                        weather_info['풍속'] = f'{fcst_value} m/s'

                    weather_info_list.append(weather_info)

            if not weather_info_list:  # 날씨 정보가 비어 있다면
                print("No weather information available.")
                return None  # None 반환

            return weather_info_list
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return None  # None 반환
    else:
        response.raise_for_status()

# 날씨 상태
def get_weather_status(pty_value):
    status_mapping = {
        '0': '맑음',
        '1': '비',
        '2': '비/눈',
        '3': '눈',
        '5': '빗방울',
        '6': '빗방울눈날림',
        '7': '눈날림',
    }
    return status_mapping.get(pty_value, '알 수 없음')

# 이미지 가져오기
def get_image_url(destination):
    # food.csv 파일에서 명칭에 해당하는 이미지 URL 가져오기 -> 추후에 final 파일로 변경 예정
    file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'fin_token.csv')
    df = pd.read_csv(file_path, encoding='utf-8')
    
    # 명칭에 해당하는 여행지의 이미지 URL 가져오기
    selected_image_url = df[df['title'] == destination]['firstimage'].iloc[0] if not df[df['title'] == destination].empty else None
    
    return selected_image_url


# # 날씨 api 가져오기 
# def get_weather_data(df, map_xy, place):# df : 장소목록 DF, map_xy : 위경도를 xy좌표로 변환하는 DF
#     base_url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst'
#     base_date = datetime.now().strftime('%Y%m%d')  # 받아서 넘겨야하는 것들 
    
#     # base_time
#     if datetime.now().minute >= 45:
#         base_time = str(datetime.now().strftime('%H')) + '30'
#     else:
#         if datetime.now().hour >= 11:
#             base_time = str(datetime.now().hour - 1)+'30'
#         else:
#             base_time = '0' + str(datetime.now().hour - 1)+'30'
    
#     # xy 좌표 
#     def get_nearest_xy(df, map_xy, place): # df : 장소목록 DF, map_xy : 위경도를 xy좌표로 변환하는 DF
#         target_latitude = df[df['title'] == place]['mapy'].values[0].round(2)
#         target_longitude = df[df['title'] == place]['mapx'].values[0].round(2)
#         map_xy['Distance'] = map_xy.apply(lambda row : haversine((row['위도(초/100)'],row['경도(초/100)']), 
#                                                              (target_latitude,target_longitude), unit=Unit.MILES), axis=1)
#         sorted_places = map_xy.sort_values(by='Distance')
#         nearest_x = sorted_places.iloc[0]['격자 X']
#         nearest_y = sorted_places.iloc[0]['격자 Y']
#         return [nearest_x, nearest_y]
#     x = get_nearest_xy(df, map_xy, place)[0]
#     y = get_nearest_xy(df, map_xy, place)[1]
    
#     params = {
#         'serviceKey': api_key,
#         'numOfRows' : '10',
#         'pageNo' : '1', 
#         'dataType' : 'JSON',
#         'base_date': base_date,
#         'base_time': base_time, 
#         'nx': str(x),
#         'ny': str(y)

#     }
#     response = requests.get(base_url, params=params)

#     if response.status_code == 200:
#         try:
#             data = response.json()
#         # 여기에서 데이터를 추출하고 필요한 정보를 반환
#             return data
#         except json.JSONDecodeError as e:
#             return response.content

#     else:
#         print(f"Error : {response.status_code}")
#         data = response.text
#         return data