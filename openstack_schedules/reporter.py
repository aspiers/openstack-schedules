#!/usr/bin/python

class Reporter:
    def __init__(self, solution):
        self.solution = solution

    def report(self):
        print("Report for solver: %s" % self.solution.solver)

        self.report_summary()

    def report_summary(self):
        for track_name in sorted(self.solution.tracks.keys()):
            track = self.solution.tracks[track_name]
            print("%-25s  %d %s  length %d  |%s|" %
                  (track_name,
                   track.start,
                   "to %d" % track.end if track.end > track.start else "    ",
                   track.length(),
                   self.pic(track)))

    def slot_pic(self, track, slot):
        if slot < track.start or slot > track.end:
            return ' '
        elif slot == track.start:
            return '<'
        elif slot == track.end:
            return '>'
        else:
            return '-'

    def pic(self, track):
        return "".join([
            #self.slot_pic(track, i)
            'X' if slot >= track.start and slot <= track.end
            else ' '
            for slot in range(1, 7)])
