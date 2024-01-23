import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from konlpy.tag import Okt
from django.conf import settings
from pathlib import Path
def tokenize_user_input(user_input):
    okt = Okt()
    # 불용어 설정
    stopwords_path = os.path.join(settings.BASE_DIR, 'final_projcect', 'modules', 'ko-stopwords.csv')  # 파일 경로 수정
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
    file_path = os.path.join(settings.BASE_DIR,  'final_projcect','modules', 'tfidf_matrix.pkl')
    tfidf_mat = pd.read_pickle(file_path)
    return tfidf_mat
def load_tfidf_vectorizer(filename='tfidf_vectorizer.pkl'):
    file_path = os.path.join(settings.BASE_DIR, 'final_projcect', 'modules', filename)
    tfidf_vect= pd.read_pickle(file_path)
    return tfidf_vect