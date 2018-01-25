import argparse
import glob
import os
import pandas
import re
import requests
import subprocess
import sys
import tarfile
import threading
import time
import urllib

def parse_args(args):
    parser = argparse.ArgumentParser(description='RetinaNet VoTT-train plugin.')
    parser.add_argument('--annotations', help='URL to annotations csv.', required=True, default=None, type=str)
    parser.add_argument('--model', help='URL to Azure Storage Container or AWS S3 bucket.', default=None, type=str)
    parser.add_argument('--status', help='URL to training status callback.', default=None, type=str)
    parser.add_argument('--epochs', help='Number of epochs to train for.', default=1, type=int)
    parser.add_argument('--steps', help='Number of steps within each epoch.', default=10, type=int)
    (known,unknown) = parser.parse_known_args(args)
    return known

args = parse_args(sys.argv[1:])

print("annotations: %s" % args.annotations)
print("model: %s" % args.model)
print("status: %s" % args.status)

def transform_url(url):
    path = os.path.join('files', os.path.basename(url))
    if os.path.isfile(path):
        return path
    print("Downloading %s from %s" % (path, url))
    urllib.request.urlretrieve(url, filename=path)
    return path

# The pandas dataframes should have the following columns:
# 0 url
# 1 x1
# 2 y1
# 3 x2
# 4 y2
# 5 class
if not os.path.isdir('snapshots'):
    os.mkdir('snapshots')
if not os.path.isdir('files'):
    os.mkdir('files')
annotations = pandas.read_csv(args.annotations, header=None, encoding="utf-8")
annotations[0] = annotations[0].apply(transform_url)
annotations.iloc[:,1:5] = annotations.iloc[:,1:5].astype(int)
annotations.to_csv('annotations.csv', header=None, index=False)

classes_columns =  [5]
annotations[classes_columns].drop_duplicates().sort_values(classes_columns).reset_index(drop=True).to_csv('classes.csv', header=None, index=True)
pandas.read_csv('classes.csv', header=None, encoding="utf-8").iloc[:, ::-1].to_csv('classes.csv', header=None, index=False)

class TrainStatus:
    def __init__(self):
        self.current_epoch = None
        self.total_epochs = None
        self.current_step = None
        self.steps_per_epoch = None
        self.current_epoch_eta = None
        self.loss = None
        self.regression_loss = None
        self.classification_loss = None
    def get_progress(self):
        total_steps = int(self.total_epochs) * float(self.steps_per_epoch)
        if not total_steps:
            return None
        completed_steps = (int(self.current_epoch)-1) * int(self.steps_per_epoch) + float(self.current_step)
        return completed_steps / total_steps

class TrainStdoutReader(threading.Thread):
    def __init__(self, fd, train_status):
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self.fd = fd
        self.train_status = train_status
    def run(self):
        for linebytes in iter(self.fd.readline, ''):
            if not self.train_status:
                break
            line = linebytes.decode('utf-8')
            epoch_search = re.search('Epoch (\d+)[/](\d+)', line, re.IGNORECASE)
            if epoch_search:
                self.train_status.current_epoch = epoch_search.group(1)
                self.train_status.total_epochs = epoch_search.group(2)
                print("current_epoch: %s" % self.train_status.current_epoch)
                print("total_epochs: %s" % self.train_status.total_epochs)
                print("")
                # TODO: Post status
            step_search = re.search('(\d+)[/](\d+) [[].{30}[]] - ETA: (\S+) - loss: (\S+) - regression_loss: (\S+) - classification_loss: (\S+)', line, re.IGNORECASE)
            if step_search:
                self.train_status.current_step = step_search.group(1)
                self.train_status.steps_per_epoch = step_search.group(2)
                self.train_status.current_epoch_eta = step_search.group(3)
                self.train_status.loss = step_search.group(4)
                self.train_status.regression_loss = step_search.group(5)
                self.train_status.classification_loss = step_search.group(6)
                print("Progress: %f" % self.train_status.get_progress())
                print("current_epoch_eta: %s" % self.train_status.current_epoch_eta)
                print("current_step: %s" % self.train_status.current_step)
                print("steps_per_epoch: %s" % self.train_status.steps_per_epoch)
                print("loss: %s" % self.train_status.loss)
                print("regression_loss: %s" % self.train_status.regression_loss)
                print("classification_loss: %s" % self.train_status.classification_loss)
                print("")
                # TODO: Post status

train_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'keras-retinanet/keras_retinanet/bin/train.py')
train_process = subprocess.Popen([
    'python3',
    train_path,
    '--epochs',
    str(args.epochs),
    '--steps',
    str(args.steps),
    'csv',
    'annotations.csv',
    'classes.csv'
], stdout=subprocess.PIPE)
train_status = TrainStatus()
stdout_reader = TrainStdoutReader(train_process.stdout, train_status)
stdout_reader.start()
train_exit_code = train_process.wait()
stdout_reader.train_status = None
stdout_reader.join()

if train_exit_code:
    print("train.py exited with %d" % train_exit_code)
    sys.exit(train_exit_code)

model_tgz = 'model.tgz'
with tarfile.open(model_tgz, 'w:gz') as tar:
        # TODO: Only include the latest snapshot and name it something like model.h5
        snapshots = glob.glob('snapshots/*.h5')
        last_snapshot = sorted(snapshots)[-1]
        tar.add(last_snapshot, arcname='model.h5')
        tar.add('classes.csv')
        tar.add('annotations.csv')

if args.model:
    model_url = os.path.join(args.model, model_tgz)
    print("Uploading %s to %s ..." % (model_tgz, model_url))
    curl_exit_code = subprocess.Popen(['curl', '-X', 'PUT', '-T', model_tgz, model_url]).wait()
    if curl_exit_code:
        print("\nUnable to upload with curl - got exit code %d" % curl_exit_code)
        sys.exit(curl_exit_code)
    else:
        print("\nUploaded %s to %s successfully." % (model_tgz, args.model))

sys.exit(0)
