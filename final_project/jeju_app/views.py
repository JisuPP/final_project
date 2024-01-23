
from django.shortcuts import render
from .utils import tokenize_user_input, load_tfidf_matrix, load_tfidf_vectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from django.conf import settings
from pathlib import Path


def index(request):
    return render(request, 'jeju_app/index.html')

def recommend(request):
    return render(request, 'jeju_app/recommend.html')

def introduce(request):
    return render(request, 'jeju_app/introduce.html')


# # Create your views here.
# http://localhost:8080 의 요청을 해결하는 함수 -> 이 부분도 바꿔줘야할듯
# def home(request):
#     return render(request, 'home.html')

# def about_view(request):
#     return render(request, '/about.html')  # About 페이지에 해당하는 HTML 파일로 수정

# def travel_predict(request):
#     if request.method == "POST":
#         current_location = request.POST.get('current-location', '')
#         travel_want = request.POST.get('travel-want', '')
#         travel_plan = request.POST.get('travel-plan', '')

#         # 모델링 파일에 보내줄 것들(home 에서 입력하는 data)
#         result_destinations = travel_predict_fn(current_location, travel_want, travel_plan)

#         # 결과를 JSON 형태로 반환, 앱 내에 있는 result.html 로 이동
#         return render(request, 'your_app_name/result.html', {'destinations': result_destinations})
#     else:
#         return render(request, 'your_app_name/index.html', {'result': None})

def recommendation_input(request):
    if request.method == 'POST':
        # user_input 토큰화
        user_input = request.POST['user_input']
        keyword_input = tokenize_user_input(user_input)
        # data 가져오기
        file_path = Path(settings.BASE_DIR) / 'final_project' / 'modules' / 'fin_data_weighted_token.csv'
        df = pd.read_csv(file_path, encoding='utf-8')
        # TF-IDF matrix, vect 가져오기
        tfidf_mat = load_tfidf_matrix()
        tfidf_vect = load_tfidf_vectorizer()
        keyword_input_mat = tfidf_vect.transform([' '.join(keyword_input)])
        keyword_input_sim = cosine_similarity(keyword_input_mat, tfidf_mat)
        keyword_input_ind = keyword_input_sim.argsort()[:, ::-1]
        # 결과 DataFrame 생성
        result_df_tfidf = df[['명칭', 'weighted_평점', '개요']].iloc[keyword_input_ind[0, :10]].sort_values('weighted_평점', ascending=False)[:7]
        # 결과를 HTML로 전달
        return render(request, 'jeju_app/index.html', {'result_df': result_df_tfidf})
    return render(request, 'jeju_app/index.html')