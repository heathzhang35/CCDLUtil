import time
import unittest
from DataManagement.Log import Log as Logger
from Utility.Decorators import threaded

def read_text(f):
    while True:
        line = f.readline()
        if not line:
            break
        yield line


class TestLogging(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestLogging, self).__init__(*args, **kwargs)
        self.logger = Logger("tests/Logging/log.txt")

    def setUp(self):
        f = open("tests/Logging/ex.txt", "r")
        for line in list(read_text(f)):
            self.logger.info(line)
        f.close()
        time.sleep(3)
        self.logger.stop_logging()

    def test_same_log(self):
        # blocking call
        str_expected = None
        str_actual = None
        with open("tests/Logging/ex.txt", "r") as str_expected_f:
            str_expected = str_expected_f.read()
        with open("tests/Logging/log.txt", "r") as str_actual_f:
            str_actual = str_actual_f.read()
        self.assertEqual(str_expected, str_actual)


if __name__ == "__main__":
    unittest.main()
            
        
