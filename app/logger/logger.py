import logging
import json
import time

"""
    A custom logging class that provides structured JSON logging for applications.

    This class is designed to create a logger that outputs logs in a structured JSON format, making it easier to parse and analyze logs in systems that require structured log data, such as ELK (Elasticsearch, Logstash, Kibana) stacks or other log management solutions.

    Attributes:
        var_logger (logging.Logger): The internal logger instance used for logging messages.

    Methods:
        __init__(name='log', log_level='DEBUG'):
            Initializes the Logger with a specified name and log level. Sets up the JSON formatter and stream handler.
        
        get_logger():
            Returns the configured logger instance for use in other parts of the application.
    """


class JsonFormatter(logging.Formatter):
    def format(self, record):
        # time with nanoseconds
        current_time = time.time()
        nanoseconds = f"{current_time:.9f}".split('.')[-1][:9]  # Extract nanoseconds

        # Format time with nanoseconds
        formatted_time = self.formatTime(record, "%Y-%m-%dT%H:%M:%S") + '.' + nanoseconds + 'Z'

        log_record = {
            "@timestamp": formatted_time,
            "@version": "1",
            "message": record.getMessage(),
            "logger_name": record.name,
            "thread_name": record.threadName,
            "level": record.levelname,
            "file_name": record.filename,
            "line_no": record.lineno,
            "function_name": record.funcName,
            "application": "Redhat-Hackathon-Opportunity-Product-Data"
        }
        return json.dumps(log_record)


class Logger:

    def __init__(self, name='log', log_level='DEBUG'):
        formatter = JsonFormatter()
        self.var_logger = logging.getLogger(name)
        self.var_logger.setLevel(log_level)

        # create stream handler which logs even debug messages
        stream_handler = logging.StreamHandler()

        # create formatter and add it to the handlers
        # formatter = logging.Formatter('%(name)-6s %(asctime)s %(levelname)-6s %(filename)s->%(funcName)s():%(lineno)s thread:%(thread)-8d - %(message)s')
        stream_handler.setFormatter(formatter)
        #stream_handler.setFormatter(formatter)

        # add the handler to the logger
        self.var_logger.addHandler(stream_handler)

    def get_logger(self):
        return self.var_logger
