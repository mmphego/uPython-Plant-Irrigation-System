import logging
import os
import sys


class LoggingClass:
    @property
    def logger(self):
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - %(module)s - "
            "%(pathname)s : %(lineno)d - %(message)s"
        )
        name = ".".join([os.path.basename(sys.argv[0]), self.__class__.__name__])
        logging.basicConfig(format=log_format)
        return logging.getLogger(name)
