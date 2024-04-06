# Импорт вашей задачи из приложения app
from app.tasks import send_get_request

result = send_get_request.delay('https://jsonplaceholder.typicode.com/posts/1')

response = result.get()

print(response)
