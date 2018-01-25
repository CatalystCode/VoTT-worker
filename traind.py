#!/usr/bin/env python3

import os
import time
import threading
import json
import subprocess

from dotenv import load_dotenv
from azure.storage.queue.queueservice import QueueService
from azure.servicebus import ServiceBusService
from azure.servicebus.models import Message
from tempfile import TemporaryDirectory
from azure.common import AzureMissingResourceHttpError

from vott.tasks import ServiceBusTaskSource
from vott.tasks import StorageQueueTaskSource

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.isfile(dotenv_path):
    load_dotenv(dotenv_path)

receive_sleep_in_seconds = int(os.environ.get('VOTT_RECEIVE_SLEEP_IN_SECONDS', '30'))

if __name__ == '__main__':
    if not (ServiceBusTaskSource.is_supported() or StorageQueueTaskSource.is_supported()):
        print("No supported task sources configured. Please set environment variables required for either ServiceBusTaskSource or StorageQueueTaskSource.")
        exit(10)
    print("Accessing task queue...")
    source = ServiceBusTaskSource() if ServiceBusTaskSource.is_supported() else StorageQueueTaskSource()
    print("Fetching tasks from %s..." % source)
    while True:
        tasks = source.receive()
        if not tasks:
            print("No new tasks, sleeping.")
            time.sleep(receive_sleep_in_seconds)
            continue
        for task in tasks:
            with TemporaryDirectory() as sandbox:
                print("Processing using sandbox: %s" % sandbox)
                task.keep_alive()
                exit_code = task.train(sandbox)
                if exit_code:
                    print("Non-zero exit code from training, so not comitting task.")
                else:
                    print("Committing task %s" % task)
                    task.commit()
