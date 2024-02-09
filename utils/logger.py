

import logging
import sys
from pathlib import Path
#from typing import IO
# Annotation imports
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Dict,
    List,
    Tuple,
    Type,
    IO
)

if TYPE_CHECKING:
    pass


#print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

class Logger(object):

    level_name_mapping:Dict[str, int] = logging.getLevelNamesMapping()

    def __init__(self, name:str, level: int = logging.NOTSET) -> None:
        """
        Initialize a logger

        Parameters
        ----------
            name : str
                Name of the logger

            level : int = 0
                Log level to use. 
                    DEBUG =< 10
                    INFO =< 20
                    WARN =< 30
                    ERROR =< 40
        """

        self.name = name

        logging.basicConfig(
          format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
          level=level,
          datefmt="%H:%M:%S",
          stream=sys.stderr,
        )

        #logger = logging.getLogger("areq")
        logging.getLogger("chardet.charsetprober").disabled = True


        self._logger = logging.getLogger(name)

        #print("Logger {name} set to level {level}".format(name=name, level=level))


    @staticmethod
    def get_level_name(level):
        """
        Return the logging level name based on the value provided. The
        logging.getLevelName() function only returns the names if the
        value provided is in the _levelToName mapping, but it doesn't
        return a name if it's between any of thoes values. This does
        just that.
        """

        # return logging.getLevelName(level)
        if level >= logging.CRITICAL:
            return "CRITICAL"

        if level >= logging.ERROR:
            return "ERROR"

        if level >= logging.WARNING:
            return "WARNING"

        if level >= logging.INFO:
            return "INFO"

        if level >= logging.DEBUG:
            return "DEBUG"

        return "NOTSET"


        

    def level(self):
        return self._logger.getEffectiveLevel()

    def level_name(self):
        return logging.getLevelName(self._logger.getEffectiveLevel())

    def set_level(self, level: int = 0):
        self._logger.setLevel(level)

        self._logger.debug(f"Verbosity of {self.name} logger to {level}")

    # Log level 50 (CRITICAL)
    def critical(self, log_entry: str) -> None:
        self._logger.critical(log_entry)


    # Log level 50 (FATAL)
    def fatal(self, log_entry: str) -> None:
        self._logger.fatal(log_entry)


    # Log level 50 (EXCEPTION)
    def exception(self, log_entry: str) -> None:
        self._logger.exception(log_entry)


    # Log level 40 (ERROR)
    def error(self, log_entry: str) -> None:
        self._logger.error(log_entry)


    # Log level 30 (WARN)
    def warn(self, log_entry: str) -> None:
        self._logger.warn(log_entry)


    # Log level 20 (INFO)
    def info(self, log_entry: str) -> None:
        self._logger.info(log_entry)


    # Log level 10 (DEBUG)
    def debug(self, log_entry: str) -> None:
        self._logger.debug(log_entry)


    def log(self, level, msg, *args, **kwargs):
        self._logger.log(level, msg)

