import logging
import sys

LEVELS = {  "DEBUG"   : logging.DEBUG,
            "INFO"    : logging.INFO,
            "WARNING" : logging.WARNING,
            "ERROR"   : logging.ERROR,
            "CRITICAL": logging.CRITICAL }

COLORS = {  "DEBUG"   : "\033[94m",
            "INFO"    : "\033[92m",
            "WARNING" : "\033[93m",
            "ERROR"   : "\033[91m",
            "CRITICAL": "\033[91m",
            "END"     : "\033[0m"  }


class logger(object):
    def __init__(self, filename):
        #set up the logger
        #configure filename, level, and message format
        logging.basicConfig(filename="logs/"+filename, level=logging.INFO, format='%(asctime)s %(levelname)s:\t %(message)s') #timestamp, message
        #instantiate a root logger object 
        self.my_logger = logging.getLogger()
        #create an stdout logger to print the messages 
        output = logging.StreamHandler(sys.stdout)
        #set level for output (same as root logger)
        output.setLevel(logging.INFO)
        #set format for output logger
        formatter = logging.Formatter(filename+'    %(asctime)s %(levelname)s:\t %(message)s')
        output.setFormatter(formatter)
        #add the output to the root logger
        self.my_logger.addHandler(output) #now log messages will also be printed to the terminal

    def log(self, message, level):
        self.my_logger.log(LEVELS[level], "%s%s%s" % (COLORS[level], message, COLORS["END"]))
