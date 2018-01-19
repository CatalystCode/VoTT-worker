import os
import time
import threading
import json
import subprocess
import sys

from azure.storage.queue.queueservice import QueueService
from azure.servicebus import ServiceBusService
from azure.servicebus.models import Message

keep_alive_interval_in_seconds = int(os.environ.get('VOTT_KEEP_ALIVE_IN_SECONDS', '1'))
default_plugin_name = os.environ.get('VOTT_KEEP_PLUGIN_NAME', 'hello-world')
default_plugin_url = os.environ.get('VOTT_KEEP_PLUGIN_URL', None)

class Task:
    '''
    Represents a queued training task.
    '''
    def __init__(self, source, content, user_info):
        self.source = source
        self.content = content
        self.user_info = user_info
        self.complete = False
    def __str__(self):
        return str(self.content)
    def train(self, sandbox):
        # TODO: Download/initialize configured plugin.
        plugin_name = self.content['plugin'] if 'plugin' in self.content else default_plugin_name
        plugin_url = self.content['plugin_url'] if 'plugin_url' in self.content else default_plugin_url
        if plugin_url:
            # TODO: Download/update plugin (git clone or git update)
            print("Updating plugin %s from %s ..." % plugin_name, plugin_url)
        else:
            print("Using plugin %s..." % plugin_name)
        print("Processing %s" % self.content)
        path_to_plugin = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'plugins', plugin_name, 'plugin.py')
        plugin_argv = [
            'python3',
            path_to_plugin
        ]
        for key, value in self.content.items():
            plugin_argv.append("--%s" % key)
            plugin_argv.append(value)
        plugin_process = subprocess.Popen(plugin_argv, cwd=sandbox)
        return plugin_process.wait()
    def commit(self):
        self.source.commit(self)
        self.complete = True
    def queue_keep_alive(self):
        threading.Timer(keep_alive_interval_in_seconds, lambda:self.keep_alive()).start()
    def keep_alive(self):
        if self.complete:
            return
        self.source.keep_alive(self)
        self.queue_keep_alive()
class TaskSource:
    '''
    Abstract class to allow switching between Azure Storage Queues or Azure
    Service Bus (or something else).
    '''
    @classmethod
    def is_supported(self):
        return False
    def receive(self):
        '''
        To be implemented by subclasses as a way to provide task(s) from either
        Azure Storage Queues or Azure Service Bus.
        '''
        raise Exception("Unimplemented")
    def commit(self, task):
        '''
        To be implemented by subclasses as a way to mark a given task as
        complete or deleted.
        '''
        raise Exception("Unimplemented")
    def keep_alive(self, task):
        '''
        To be implemented by subclasses as a way to tell the queueing system
        that the given task is still being worked on.
        '''
        raise Exception("Unimplemented")

class StorageQueueTaskSource(TaskSource):
    '''
    Azure Storage Queue implementation of TaskSource.
    '''
    def __init__(self):
        self.queue = QueueService(
            account_name=self.storage_account_name(),
            account_key=self.storage_key()
        )
        self.queue_name = os.environ.get('AZURE_STORAGE_QUEUE_NAME', 'training')
        self.queue_message_count = int(os.environ.get('AZURE_STORAGE_QUEUE_MESSAGE_COUNT', '1'))
    
    @classmethod
    def storage_account_name(self):
        return os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
    
    @classmethod
    def storage_key(self):
        return os.environ.get('AZURE_STORAGE_KEY')

    def __str__(self):
        return "Storage Queue (%s)" % self.storage_account_name()
    
    @classmethod
    def is_supported(self):
        return self.storage_account_name() and self.storage_key()

    def receive(self):
        messages = self.queue.get_messages(self.queue_name, self.queue_message_count)
        return [Task(source=self, content=json.loads(message.content), user_info=message) for message in messages]

    def keep_alive(self, task):
        result = self.queue.update_message(self.queue_name, task.user_info.id, task.user_info.pop_receipt, keep_alive_interval_in_seconds)
        task.user_info.pop_receipt = result.pop_receipt
    
    def commit(self, task):
        self.queue.delete_message(self.queue_name, task.user_info.id, task.user_info.pop_receipt)

class ServiceBusTaskSource(TaskSource):
    '''
    Azure Service Bus implementation of TaskSource.
    '''
    def __init__(self):
        self.service_bus = ServiceBusService(ServiceBusTaskSource.service_bus_namespace(),
                                shared_access_key_name=os.environ.get('AZURE_SERVICE_BUS_ACCESS_KEY_NAME'),
                                shared_access_key_value=os.environ.get('AZURE_SERVICE_BUS_ACCESS_KEY_VALUE'))
        self.queue_name = os.environ.get('AZURE_SERVICE_BUS_QUEUE_NAME', 'training')
    @classmethod
    def service_bus_namespace(self):
        return os.environ.get('AZURE_SERVICE_BUS_NAMESPACE')
    @classmethod
    def is_supported(self):
        return self.service_bus_namespace()
    def receive(self):
        message = self.service_bus.receive_queue_message(self.queue_name)
        if message:
            return Task(source=self, content=None, user_info=message)
        return None
    def commit(self, task):
        task.user_info.delete()
