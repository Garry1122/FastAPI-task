# Ваш файл views.py
from django.shortcuts import render
from .tasks import send_get_request, send_post_request

def index(request):
    # Вызываем Celery задачу для отправки GET запроса
    get_response_task = send_get_request.delay('https://jsonplaceholder.typicode.com/posts/1')
    # Вызываем Celery задачу для отправки POST запроса (можно также передать данные)
    # post_response_task = send_post_request.delay('https://jsonplaceholder.typicode.com/posts', data={'title': 'foo', 'body': 'bar', 'userId': 1})
    
    # Получаем результаты выполнения задач
    get_response = get_response_task.get()
    # post_response = post_response_task.get()
    
    return render(request, 'index.html', {'get_response': get_response})
