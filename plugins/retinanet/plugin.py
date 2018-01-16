import argparse
import sys
import time

def parse_args(args):
    parser = argparse.ArgumentParser(description='RetinaNet VoTT-train plugin.')
    parser.add_argument('--annotations', help='URL to annotations csv.', default=None, type=str)
    parser.add_argument('--model', help='URL to Azure Storage Container or AWS S3 bucket.', default=None, type=str)
    parser.add_argument('--status', help='URL to training status callback.', default=None, type=str)
    return parser.parse_args(args)


args = parse_args(sys.argv[1:])

print("annotations: %s" % args.annotations)
print("model: %s" % args.model)
print("status: %s" % args.status)

time.sleep(30)
sys.exit(0)
