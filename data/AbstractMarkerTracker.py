import abc


class AbstractMarkerTracker(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_players_positions(self, frame):
        pass