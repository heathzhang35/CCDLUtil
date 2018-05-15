"""
A class for generating log files.

This takes data from a queue and writes it to disk.  This is typically event data from
an experiment (not EEG data).

"""
from queue import Queue
from CCDLUtil.Utility.Decorators import threaded


class Log(object):

    """
    A log object is responsible for reading items from a queue and writing them to file.
    """

    def __init__(self, subject_log_file_path, verbose=False, header=None):
        """
        Logs all items to file.  Files are taken from the log_queue and written to the file specified by
        subject_log_file_path.
        :param subject_log_file_path: String. where to save the file
        :param log_queue: queue to read items from
        :param header:
        """
        self.f = open(subject_log_file_path, 'w')
        self.log_queue = Queue()
        self._verbose = verbose
        if header is not None:
            self.f.write(header)
        # create new thread and start logging to file
        self.is_logging = False
        self._start_log()

    def info(self, message):
        """
        Put message into queue for logging. Client of this class should call this method to log information

        :param message: the message to be logged
        """
        self.log_queue.put(message)

    @staticmethod
    def _append_log(body) -> str:
        assert type(body) is str
        return body if body.endswith("\n") else body + "\n"

    @threaded(True)
    def _start_log(self):
        """
        Starts reading items from the queue.  All items passed to the queue must be a string or it will be converted
        (raising a warning).  If no new line is at the end of the string, one will be added.

        The buffer is immediately flushed after every write.

        :param verbose: If verbose, will print the items to console.  Defaults to False.
        :return: Runs forever.  Kill thread to terminate.
        """
        self._is_logging = True
        while self._is_logging:
            body = Log._append_log(self.log_queue.get())
            if self._verbose:
                print(body)
            self.f.write(body)
            self.f.flush()
        print("log quit")

    def stop_logging(self):
        self._is_logging = False        

    def is_logging(self) -> bool:
        return self._is_logging
        
