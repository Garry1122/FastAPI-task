from celery import shared_task
import requests

@shared_task
def send_get_request(url):
    response = requests.get(url)
    return response.text

@shared_task
def send_post_request(url, data):
    response = requests.post(url, data=data)
    return response.text
