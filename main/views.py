from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from . import models
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CommentForm

def index(request):
    cards=models.Card.objects.all()
    return render(request, 'main/index.html',{ 'cards': cards })

def createCard(request):
    if request.method == "POST":
        models.Card.objects.create(title=request.POST["title"], description=request.POST["desc"], date=request.POST["date"])
        return redirect("index")
    return render(request, "main/create.html",{})

def article_detail(request, pk):
    from django.http import JsonResponse
    try:
        card = models.Card.objects.get(pk=pk)
        print(f"Найдена карточка: {card.title}")  # Проверьте консоль сервера
        
        # Тестовый вывод в JSON
        if 'debug' in request.GET:
            return JsonResponse({
                'id': card.id,
                'title': card.title,
                'description': card.description,
                'date': str(card.date)
            })
            
        return render(request, 'main/article_detail.html', {'card': card})
    except models.Card.DoesNotExist:
        return render(request, 'main/404.html', status=404)