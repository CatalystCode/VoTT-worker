import threading
import sys
import argparse

def parse_args(args):
    parser = argparse.ArgumentParser(description='Hello World VoTT-train plugin.')
    parser.add_argument('--annotations', help='URL to annotations csv.', default=None, type=str)
    parser.add_argument('--model', help='URL to Azure Storage Container or AWS S3 bucket.', default=None, type=str)
    parser.add_argument('--status', help='URL to training status callback.', default=None, type=str)
    return parser.parse_args(args)


args = parse_args(sys.argv[1:])

print("hello-world args:")
print("  annotations: %s" % args.annotations)
print("  model: %s" % args.model)
print("  status: %s" % args.status)

hello_count = 0
def hello():
    global hello_count
    print("hello, world (%s)" % hello_count)
    hello_count+=1
    if hello_count < 10:
        queue_hello()
def queue_hello():
    threading.Timer(3.0, hello).start()

hello()

