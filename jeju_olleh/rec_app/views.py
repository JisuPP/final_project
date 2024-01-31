import os
import pandas as pd
from .utils import tokenize_user_input, load_tfidf_matrix, load_tfidf_vectorizer, get_nearest_weather_data, get_address_info, lat_long_distance, get_image_url
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
from django.shortcuts import render

def rec_input(request):
    
    if request.method == 'POST':
        # user_input 토큰화
        user_input = request.POST['user_input']
        keyword_input = tokenize_user_input(user_input)

        # data 가져오기
        file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'fin_data_weighted_token.csv')
        df = pd.read_csv(file_path, encoding='utf-8')

        # TF-IDF matrix, vect 가져오기
        tfidf_mat = load_tfidf_matrix()
        tfidf_vect = load_tfidf_vectorizer()

        keyword_input_mat = tfidf_vect.transform([' '.join(keyword_input)])
        keyword_input_sim = cosine_similarity(keyword_input_mat, tfidf_mat)
        keyword_input_ind = keyword_input_sim.argsort()[:, ::-1]

        # 결과 DataFrame 생성
        result_df_tfidf = df.iloc[keyword_input_ind[0, :10]].sort_values('weighted_평점', ascending=False)[:7]

        if not result_df_tfidf.empty:
            
            #이미지 URL 추가
            result_df_tfidf['selected_image_url'] = result_df_tfidf['명칭'].apply(get_image_url)

            # 날씨 정보 추가
            result_df_tfidf['날씨'] = result_df_tfidf.apply(lambda x: get_nearest_weather_data(x['명칭']), axis=1)

            # 결과를 HTML로 전달
            return render(request, 'rec_app/rec_result.html', {'result_df': result_df_tfidf})
    
    # GET 요청에 대한 처리를 추가
    return render(request, 'rec_app/rec_input.html')

def detail(request, destination):
    # 여기에서 destination은 선택한 여행지의 명칭입니다.
    file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'fin_data_weighted_token_map.csv')
    df = pd.read_csv(file_path, encoding='utf-8')

    # '명칭'이라는 열이 있을 경우
    selected_destination = df[df['명칭'] == destination].iloc[0]

    # 이미지 URL 가져오기
    selected_destination['selected_image_url'] = get_image_url(destination)

    return render(request, 'rec_app/detail.html', {'selected_destination': selected_destination})

def about(request):
    # About 페이지에 대한 뷰 로직을 작성합니다.
    return render(request, 'rec_app/about.html')

def place_rec(request):
    # place_rec 페이지에 대한 뷰 로직을 작성합니다.
    return render(request, 'rec_app/place_rec.html')


def rec_place(request):
    if request.method == 'POST':
        # 사용자가 입력한 정보 가져오기
        user_input = request.POST.get('user_input')
        user_address = request.POST.get('address_input')  # 수정된 부분

        # 사용자의 주소 정보 가져오기
        user_coordinates = get_address_info(user_address)

        if not user_coordinates.empty:
            user_latitude = user_coordinates['Latitude'].iloc[0]
            user_longitude = user_coordinates['Longitude'].iloc[0]

            # 데이터 가져오기
            file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'fin_data_weighted_token.csv')
            df = pd.read_csv(file_path, encoding='utf-8')

            # TF-IDF matrix, vectorizer 가져오기
            tfidf_mat = load_tfidf_matrix()
            tfidf_vect = load_tfidf_vectorizer()

            # 사용자 입력 키워드에 대한 TF-IDF 값 계산
            keyword_input_mat = tfidf_vect.transform([user_input])

            keyword_input_sim = cosine_similarity(keyword_input_mat, tfidf_mat)
            keyword_input_ind = keyword_input_sim.argsort()[:, ::-1]

            # 결과 DataFrame 생성
            result_df = df.iloc[keyword_input_ind[0]]  # 수정된 부분

            # 15km 이내의 장소 필터링
            filtered_df = result_df[result_df.apply(lambda x: lat_long_distance(x['위도'], x['경도'], user_latitude, user_longitude) <= 15, axis=1)]

            recommended_places = filtered_df.head(5)

            # 결과를 HTML로 전달
            return render(request, 'rec_app/place_result.html', {'result_df': recommended_places})

    return render(request, 'rec_app/place_rec.html')

def map(request):
    # 관광지 전체 목록 지도로 구성
    return render(request, 'rec_app/map.html')
