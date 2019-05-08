class Track:
    __slots__ = [
        "track_name", "min_length", "max_length", "start", "end", "overlap"
    ]

    def __init__(self, track_name):
        self.track_name = track_name
        self.overlap = {}

    def length(self):
        return self.end - self.start + 1
