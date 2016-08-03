from __future__ import absolute_import

import os

from celery import Celery
from celery import Task
from random import random

from svggen.api import FoldedComponent



# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robotBuilder.settings')

from django.conf import settings  # noqa

app = Celery('proj')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)



@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))



class StoreNumber(Task):
    _numbers = None

    @property
    def numbers(self):
        if self._numbers is None:
            self._numbers = FoldedComponent.FoldedComponent()
        return self._numbers

@app.task(base=StoreNumber)
def getnumbers():
    return getnumbers.numbers

@app.task(base=StoreNumber)
def addnumber():
    string = 'r'+random()
    if addnumber.numbers is not None:
        addnumber.numbers.addSubcomponent(string, 'Rectangle')
    return addnumber.numbers