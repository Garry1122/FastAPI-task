import json
import logging

from rest_framework.generics import GenericAPIView

from app.api.serializers import FacebookScrupperSerializer
from lib.redis_client import RedisOperation
import datetime
import json
import base64
import logging
import re
from datetime import datetime
import subprocess

from app import celery_app
from rest_framework import status as statuses
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from celery import states
from .tasks import fb_scrup
redis_client = RedisOperation()
logger = logging.getLogger(__name__)


class vROpsBaseAPIView(GenericAPIView):
    def get_task_state(self, task_prefix):
        task_id = self.request.query_params.get("task_id", None)
        task_status = self.request.query_params.get("status", None)
        if task_id:
            task = redis_client.get(f"{task_prefix}{task_id}")
            if task:
                result = json.loads(task)
                return Response(result, status=status.HTTP_200_OK)
            else:
                # ToDo inspect queue as well
                with celery_app.pool.acquire(block=True) as conn:
                    tasks = conn.default_channel.client.lrange('celery', 0, -1)
                    decoded_tasks = []
                for task in tasks:
                    j = json.loads(task)
                    body = json.loads(base64.b64decode(j['body']))
                    data = body[1]
                    if data['task_id'] == task_id and data['task_name'] == task_prefix:
                        result = {
                            "status": "PENDING",
                            "result": {
                                "start_time": "",
                                "end_time": "",
                                "log": "",
                                "data": None,
                                "parameters": data['payload']
                            },
                            "traceback": None,
                            "children": [],
                            "date_done": None,
                            "task_id": data['task_id']
                        }
                        return Response(result, status=status.HTTP_200_OK)
                return Response("Task not found", status=status.HTTP_404_NOT_FOUND)

        res = []
        for key in redis_client.scan_iter(f"{task_prefix}*"):
            item = json.loads(redis_client.get(key))
            if task_status:
                if item["status"] == task_status:
                    res.append(item)
            else:
                res.append(item)

        return Response(res, status=status.HTTP_200_OK)

    def terminate_task(self, task_prefix=None):
        task_id = self.request.query_params.get("task_id", None)
        if task_id:
            inspect = celery_app.control.inspect()
            active_tasks = inspect.active()
            if active_tasks:
                for worker in active_tasks.keys():
                    for task in active_tasks[worker]:
                        if task['id'] == task_id:
                            celery_app.control.terminate(task_id, signal='SIGUSR1')
                            return Response(status.HTTP_204_NO_CONTENT)

            task = redis_client.get(f"{task_prefix}{task_id}")
            if task:
                result = json.loads(task)
                if result['status'] == states.PENDING:
                    result['status'] = states.REVOKED
                    result['result']['return_code'] = 1
                    result['result']['error_details'] = "Revoked manually"
                    result['result']['error_type'] = "Exception"
                    redis_client.set(f"{task_prefix}{task_id}", json.dumps(result))
                return Response(status.HTTP_204_NO_CONTENT)
            return Response("Task not found", status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("task_id : required parameter", status=status.HTTP_400_BAD_REQUEST)

    def start_task(self, task_function, *args, **kwargs):
        suspend_duration = redis_client.get("suspend_duration")
        if suspend_duration:
            remaining_time = redis_client.ttl("suspend_duration")
            task = task_function.apply_async(args, kwargs, countdown=remaining_time, )
            task_status = {
                "status": "PENDING",
                "result": {
                    "start_time": str(
                        datetime.datetime.now()
                        + datetime.timedelta(seconds=remaining_time)
                    ),
                    "end_time": None,
                    "log": None,
                    "data": None,
                    "parameters": kwargs['payload'],
                    "return_code": None,
                },
                "traceback": None,
                "children": [],
                "date_done": None,
                "task_id": f"{task.id}",
            }
            redis_client.set(f"{task_function.name}{task.id}", json.dumps(task_status))
        else:
            task = task_function.delay(*args, **kwargs)
        return Response({"task_id": task.id}, status.HTTP_201_CREATED)


class ScrupFacebookPost(vROpsBaseAPIView):
    serializer_class = FacebookScrupperSerializer

    def get(self, request):
        return self.get_task_state(fb_scrup.name)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            return Response(
                serializer.errors,
                status=statuses.HTTP_400_BAD_REQUEST,
            )
        return self.start_task(fb_scrup, dict(serializer.validated_data), payload=serializer.validated_data)

    def delete(self, request):
        return self.terminate_task(fb_scrup.name)

