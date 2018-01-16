import argparse
import sys
import time
import pandas
import os
import urllib
import subprocess

def parse_args(args):
    parser = argparse.ArgumentParser(description='RetinaNet VoTT-train plugin.')
    parser.add_argument('--annotations', help='URL to annotations csv.', required=True, default=None, type=str)
    parser.add_argument('--model', help='URL to Azure Storage Container or AWS S3 bucket.', default=None, type=str)
    parser.add_argument('--status', help='URL to training status callback.', default=None, type=str)
    return parser.parse_args(args)

args = parse_args(sys.argv[1:])

print("annotations: %s" % args.annotations)
print("model: %s" % args.model)
print("status: %s" % args.status)

def transform_url(url):
    path = os.path.join('files', os.path.basename(url))
    if os.path.isfile(path):
        return path
    print("Dowloading to %s: %s" % (path, url))
    urllib.request.urlretrieve(url, filename=path)
    return path

# The pandas dataframes should have the following columns:
# 0 url
# 1 x
# 2 y
# 3 width
# 4 height
# 5 class
if not os.path.isdir('files'):
    os.mkdir('files')
annotations = pandas.read_csv(args.annotations, header=None, encoding="utf-8")
annotations[0] = annotations[0].apply(transform_url)
annotations.iloc[:,1:5] = annotations.iloc[:,1:5].astype(int)
annotations.to_csv('annotations.csv', header=None, index=False)

# TODO: Sort rows and create new indexes.
classes_columns =  [5]
annotations[classes_columns].drop_duplicates().sort_values([5]).reset_index(drop=True).to_csv('classes.csv', header=None, index=True)

plugin_process = subprocess.Popen([
    'python3',
    'keras-retinanet/keras_retinanet/bin/train.py',
    '--epochs',
    '10',
    '--steps',
    '100',
    'csv',
    'annotations.csv',
    'classes.csv'
])
sys.exit(plugin_process.wait())
