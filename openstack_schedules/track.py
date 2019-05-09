class Track:
    __slots__ = [
        "track_name",
        "min_length", "max_length",
        "start", "end",
        "overlaps", "total_overlap"
    ]

    def __init__(self, track_name):
        self.track_name = track_name
        self.overlaps = {}
        self.total_overlap = 0

    def length(self):
        return self.end - self.start + 1

    def add_overlap(self, other_track_name, num_slots):
        '''Make sure not to call this multiple times with the same track.
        '''
        self.overlaps[other_track_name] = num_slots
        self.total_overlap += num_slots
