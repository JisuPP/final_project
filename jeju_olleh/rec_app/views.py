from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .utils import tokenize_user_input, load_tfidf_matrix, load_tfidf_vectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os
from django.conf import settings
from pathlib import Path

def recommendation_input(request):
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
        result_df_tfidf = df[['명칭', 'weighted_평점', '개요']].iloc[keyword_input_ind[0, :10]].sort_values('weighted_평점', ascending=False)[:7]
        # 결과를 HTML로 전달
        return render(request, 'rec_app/recommendation_result.html', {'result_df': result_df_tfidf})
    return render(request, 'rec_app/recommendation_input.html')

