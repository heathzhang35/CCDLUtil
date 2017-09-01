"""
This file contains decorators for use in various contexts
"""

import threading


# calls the given function (fn) in a new thread
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper
