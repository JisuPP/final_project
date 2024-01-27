# rec_app/views.py

from django.shortcuts import render
from .utils import tokenize_user_input, load_tfidf_matrix, load_tfidf_vectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os
from django.conf import settings

def recommendation_input(request):
    if request.method == 'POST':
        # user_input 토큰화
        user_input = request.POST['user_input']
        # address_input도 가져오기 
        address_input = request.POST['address_input']

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
        result_df_tfidf = df[['명칭', 'weighted_평점', '개요']].iloc[keyword_input_ind[0, :10]].sort_values('weighted_평점', ascending=False)[:7]
        # 결과를 HTML로 전달
        return render(request, 'rec_app/rec_result.html', {'result_df': result_df_tfidf})
    return render(request, 'rec_app/recommendation_input.html')

def rec_result(request):
    # 여기에서 추천 결과 데이터를 가져오도록 수정
    file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'fin_data_weighted_token.csv')
    df = pd.read_csv(file_path, encoding='utf-8')
    # 예시로 처음 7개 데이터를 가져옴. 실제로는 어떤 데이터를 가져올지 로직에 맞게 수정 필요
    result_df = df[['명칭', 'weighted_평점', '개요']].head(7)
    return render(request, 'rec_app/rec_result.html', {'result_df': result_df})


def detail(request, destination):
    # 여기에서 destination은 선택한 여행지의 명칭입니다.
    file_path = os.path.join(settings.BASE_DIR, 'jeju_olleh', 'modules', 'fin_data_weighted_token.csv')
    df = pd.read_csv(file_path, encoding='utf-8')
    selected_destination = df[df['명칭'] == destination].iloc[0]
    return render(request, 'rec_app/detail.html', {'selected_destination': selected_destination})

def about(request):
    # About 페이지에 대한 뷰 로직을 작성합니다.
    return render(request, 'rec_app/about.html')
