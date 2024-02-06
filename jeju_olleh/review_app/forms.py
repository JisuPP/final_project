from django import forms
from .models import Review
# 1. 입력 데이터 검증 과정 X
# 2. HTML 만들기 귀찮다
class ReviewForm(forms.ModelForm): # 이름 모델과 맞춰서 생성
    # 0. fields에 적힌 컬럼에 대해서만 이라는 조건이 있다.
    # 1. 입력 데이터 검증해줌
    # 2. HTML(input,textarea,label등...) 을 생성 (입력 귀찮으니까!)
     # 상수(값이 초기화/할당 이후 절대 변하면 안된다는 뜻)
    CHOICES = [
        (1, '*'),
        (2, '**'),
        (3, '***'),
        (4, '****'),
        (5, '*****'),
    ]
    rate = forms.ChoiceField(
        widget=forms.Select(),
        choices = CHOICES
    )
    content = forms.CharField(
        widget=forms.Textarea(),
        min_length=5,
        label=''
     )
    class Meta: # 아래부터 코드의 생김새가 이런 이유는 그냥 장고가 그렇게 쓰게 만들어서..
        model = Review
        fields = ['content','rate']
        exclude = ('user', 'title')
        # fields = '__all__' # title, content 필드 모두에 대해 케이스를 끼우겠다는 의미/ 여기 들어가는 옵션 알아보기









