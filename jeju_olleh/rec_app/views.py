import os
import pandas as pd
from .utils import tokenize_user_input, load_tfidf_matrix, load_tfidf_vectorizer, get_nearest_weather_data, get_address_info, lat_long_distance, get_image_url, take_modeldf, take_djangodf, create_folium_map
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
from django.shortcuts import render
import csv
from django.http import HttpResponse
from .models import DjangoDf


def home(request):
    return render(request, 'rec_app/home.html')

def rec_input(request):
    
    if request.method == 'POST':
        # user_input 토큰화
        user_input = request.POST['user_input']
        keyword_input = tokenize_user_input(user_input)

        # data 가져오기
        # file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'fin_token.csv')
        # df = pd.read_csv(file_path, encoding='utf-8')
        queryset = take_djangodf()
        # 쿼리셋을 리스트로 변환
        data = list(queryset.values())
        # 데이터프레임으로 변환
        df = pd.DataFrame(data)

        # TF-IDF matrix, vect 가져오기
        tfidf_mat = load_tfidf_matrix()
        tfidf_vect = load_tfidf_vectorizer()

        keyword_input_mat = tfidf_vect.transform([' '.join(keyword_input)])
        keyword_input_sim = cosine_similarity(keyword_input_mat, tfidf_mat)
        keyword_input_ind = keyword_input_sim.argsort()[:, ::-1]

        # 결과 DataFrame 생성
        result_df = df.iloc[keyword_input_ind[0, :10]].sort_values('rating', ascending=False)[:7]

        if not result_df.empty:

            #이미지 URL 추가
            result_df['selected_image_url'] = result_df['title'].apply(get_image_url)

            # 결과를 HTML로 전달
            return render(request, 'rec_app/rec_result.html', {'result_df': result_df})
    
    # GET 요청에 대한 처리를 추가
    return render(request, 'rec_app/rec_input.html')

def detail(request, destination):

    # 여기에서 destination은 선택한 여행지의 명칭입니다.
    # file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'fin_token.csv')
    # df = pd.read_csv(file_path, encoding='utf-8')

    queryset = take_djangodf()
    data = list(queryset.values())
    df = pd.DataFrame(data)

    # '명칭'이라는 열이 있을 경우
    selected_destination = df[df['title'] == destination].iloc[0]

    # 이미지 URL 가져오기
    selected_destination['selected_image_url'] = get_image_url(destination)
    selected_destination['weather_info'] = get_nearest_weather_data(selected_destination['title'])
    
    # 지도 가져오기
    selected_destination['map'] = create_folium_map(selected_destination)

    return render(request, 'rec_app/detail.html', {'selected_destination': selected_destination})

def about(request):
    # About 페이지에 대한 뷰 로직을 작성합니다.
    return render(request, 'rec_app/about.html')


def rec_address(request):
    if request.method == 'POST':

        # 사용자가 입력한 정보 가져오기
        user_input = request.POST['second_user_input']
        user_address = request.POST.get('address_input')
        keyword_input = tokenize_user_input(user_input)
        keyword_input = ' '.join(keyword_input)

        # 주소
        user_coordinates = get_address_info(user_address)
        user_latitude = user_coordinates['Latitude'].iloc[0]
        user_longitude = user_coordinates['Longitude'].iloc[0]

        # 데이터 가져오기
        queryset = take_modeldf()
        data = list(queryset.values())
        df = pd.DataFrame(data)

        # TF-IDF matrix, vectorizer 가져오기
        tfidf_mat = load_tfidf_matrix()
        tfidf_vect = load_tfidf_vectorizer()

        # 사용자 입력 키워드에 대한 TF-IDF 값 계산
        keyword_input_mat = tfidf_vect.transform([(keyword_input)])
        keyword_input_sim = cosine_similarity(keyword_input_mat, tfidf_mat)
        keyword_input_ind = keyword_input_sim.argsort()[:, ::-1]
        
        result_df = df.iloc[keyword_input_ind[0]]

        filtered_df = result_df[result_df.apply(lambda x: lat_long_distance(x['mapy'], x['mapx'], user_latitude, user_longitude) <= 15, axis=1)]
        filtered_df['selected_image_url'] = filtered_df['title'].apply(get_image_url)
        recommended_places = filtered_df.head(5)
        return render(request, 'rec_app/other.html', {'recommended_places' : recommended_places})
    return render(request, 'rec_app/rec_input.html')


def map(request):
    # 관광지 전체 목록 지도로 구성
    return render(request, 'rec_app/map.html')

# DB > CSV
# def export_django_df_to_csv(request):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="djangodf.csv"'
#     # CSV 파일에 쓸 필드명을 지정합니다.
#     fieldnames = ['title', 'addr1', 'rating', 'reviews', 'mapx', 'mapy', 'overview', 'firstimage', 'cat1', 'cat2', 'cat3', 'index']
#     # CSV writer를 생성합니다.
#     writer = csv.DictWriter(response, fieldnames=fieldnames)
#     # CSV 파일의 헤더를 씁니다.
#     writer.writeheader()
#     # DjangoDf 데이터를 가져와서 CSV 파일에 씁니다.
#     djangodf_items = DjangoDf.objects.all()
#     for item in djangodf_items:
#         writer.writerow({
#             'title': item.title,
#             'addr1': item.addr1,
#             'rating': item.rating,
#             'reviews': item.reviews,
#             'mapx': item.mapx,
#             'mapy': item.mapy,
#             'overview': item.overview,
#             'firstimage': item.firstimage,
#             'cat1': item.cat1,
#             'cat2': item.cat2,
#             'cat3': item.cat3,
#             'index': item.index,
#         })
#     return response


# DB > CSV
# import csv
# from django.http import HttpResponse
# from .models import ModelDf  # YourModel을 해당 모델의 실제 이름으로 바꿔야 합니다.
# def export_to_csv(request):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="your_model_data.csv"'
#     # CSV 파일에 쓸 필드명을 지정합니다.
#     fieldnames = ['title', 'weighted_rating', 'cat3', 'mapx', 'mapy', 'overview', 'index']
#     # CSV writer를 생성합니다.
#     writer = csv.DictWriter(response, fieldnames=fieldnames)
#     # CSV 파일의 헤더를 씁니다.
#     writer.writeheader()
#     # YourModel 데이터를 가져와서 CSV 파일에 씁니다.
#     your_model_items = ModelDf.objects.all()
#     for item in your_model_items:
#         writer.writerow({
#             'title': item.title,
#             'weighted_rating': item.weighted_rating,
#             'cat3': item.cat3,
#             'mapx': item.mapx,
#             'mapy': item.mapy,
#             'overview': item.overview,
#             'index': item.index,
#         })
#     return response

def find_route(request):
    locations = DjangoDf.objects.values('title', 'mapx', 'mapy')

    # HTML 페이지에 데이터 전달
    context = {'locations': locations}
    return render(request, 'rec_app/find_route.html', context)

def kakao(request):
    return render(request, 'rec_app/kakao.html')