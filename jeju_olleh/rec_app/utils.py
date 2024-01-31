import datetime, json, os, pickle, requests
import pandas as pd
from haversine import haversine, Unit
from datetime import datetime
from konlpy.tag import Okt
from django.conf import settings
from math import radians, sin, cos, sqrt, atan2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def tokenize_user_input(user_input):
    okt = Okt()
    # 불용어 설정
    stopwords_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'ko-stopwords.csv')  # 파일 경로 수정
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

def load_tfidf_matrix(filename='tfidf_matrix.pkl'):  # 파일 경로 수정
    file_path = os.path.join(settings.BASE_DIR,  'jeju_olleh','modules', 'tfidf_matrix.pkl')
    tfidf_mat = pd.read_pickle(file_path)
    return tfidf_mat

def load_tfidf_vectorizer(filename='tfidf_vectorizer.pkl'):
    file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', filename)
    tfidf_vect= pd.read_pickle(file_path)
    return tfidf_vect

def lat_long_distance(lat1, lon1, lat2, lon2):
    # 두 지점 간의 Haversine 거리를 계산합니다.
    # 지구의 반지름 (단위: km)
    R = 6371.0
    # 라디안으로 변환
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    # 위도와 경도의 차이 계산
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    # Haversine 공식 계산
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    # 거리 계산
    distance = R * c
    return distance

def get_address_info(address):
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


def get_nearest_weather_data(place):

    file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'fin_data_weighted_token.csv')
    df = pd.read_csv(file_path, encoding='utf-8')

    map_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'map_xy.csv')
    map_xy = pd.read_csv(map_path, encoding='utf-8')

    # 넘어온 위도, 경도값 변수 지정하기
    target_latitude = df[df['명칭'] == place]['위도'].round(2).iloc[0]  # 수정된 부분
    target_longitude = df[df['명칭'] == place]['경도'].round(2).iloc[0]  # 수정된 부분

    # 기존 Distance 컬럼이 존재한다면 삭제
    if 'Distance' in map_xy.columns:
        map_xy.drop('Distance', axis=1, inplace=True)

    # 해당 위도, 경도값에서 가장 가까운 지점 찾아 xy 뽑기
    map_xy['Distance'] = map_xy.apply(lambda row: haversine((row['위도(초/100)'], row['경도(초/100)']),
                                                        (target_latitude, target_longitude), unit=Unit.MILES), axis=1)

    sorted_places = map_xy.sort_values(by='Distance')
    nearest_x = sorted_places.iloc[0]['격자 X']
    nearest_y = sorted_places.iloc[0]['격자 Y']

    base_date = datetime.now().strftime('%Y%m%d')

    # base_time
    if datetime.now().minute >= 45:
        base_time = str(datetime.now().hour) + '30'
    else:
        base_time = str(datetime.now().hour - 1) + '30'

    api_key = ''

    base_url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'

    params = {
        'serviceKey': api_key,
        'numOfRows': '10',
        'pageNo': '1',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': nearest_x ,
        'ny': nearest_y
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            print(data)  # API 응답 데이터 출력
            # 여기에서 데이터를 추출하고 필요한 정보를 반환
            return data
        except json.JSONDecodeError as e:
            return response.content
    else:
        print(f"Error : {response.status_code}")
        data = response.text
        print(data)  # 에러 응답 데이터 출력
        return data

def get_image_url(destination):
    # food.csv 파일에서 명칭에 해당하는 이미지 URL 가져오기
    food_file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'food.csv')
    food_df = pd.read_csv(food_file_path, encoding='utf-8')
    
    # 명칭에 해당하는 여행지의 이미지 URL 가져오기
    selected_image_url = food_df[food_df['title'] == destination]['firstimage'].iloc[0] if not food_df[food_df['title'] == destination].empty else None
    
    return selected_image_url
