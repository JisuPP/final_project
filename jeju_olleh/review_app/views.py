from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_safe, require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Review
from .forms import ReviewForm
from django.db.models import Avg
# Create your views here.
@require_http_methods(['GET', 'POST'])
def create(request, title):
    if request.method == 'GET':
        form = ReviewForm()
    elif request.method == 'POST':
        form = ReviewForm(data=request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.title = title
            review.save()
            return redirect('review_app:index', title=title)
    return render(request, 'review_app/form.html', {
        'form' : form,
        'title' : title,
    })
@require_safe
def index(request, title):
    reviews = Review.objects.filter(title=title)
    average_rate = reviews.aggregate(avg_rate=Avg('rate'))['avg_rate']
    return render(request, "review_app/index.html", {
        'reviews': reviews,
        'title' : title,
        'average_rate': average_rate,
    })
@require_safe
def detail(request, title, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, "review_app/detail.html", {
        'review' : review,
        'title' :title
    })