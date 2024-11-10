# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from datetime import timedelta
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
from kombu import Exchange, Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.task_queues = (
    Queue('queue1', Exchange('queue1'), routing_key='queue1'),
    Queue('queue2', Exchange('queue2'), routing_key='queue2'),
    Queue('queue3', Exchange('queue3'), routing_key='queue3'),
)

# app.conf.beat_schedule = {
#     'rm_forgotpass_objs': {
#         'task': 'account.tasks.forgotPasswordTasks.removeForgotPassOTP',
#         'schedule': crontab(hour="1,13"),
#     },
#     'rm_verfication_objs': {
#         'task': 'account.tasks.verifyAccountTasks.removeVerficationAccOTP',
#         'schedule': crontab(hour="2,14"),
#     }
# }

# Add the new setting to handle connection retry on startup
app.conf.broker_connection_retry_on_startup = True

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
