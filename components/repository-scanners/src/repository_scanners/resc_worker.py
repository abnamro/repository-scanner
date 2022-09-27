# Standard Library
import abc


class RESCWorker(metaclass=abc.ABCMeta):

    def pre_work(self):
        pass

    def start(self):
        pass

    def parse_output(self):
        pass
