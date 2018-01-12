import threading

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

