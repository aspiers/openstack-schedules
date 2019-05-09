#!/usr/bin/python

class Reporter:
    def __init__(self, solution):
        self.solution = solution

    def report(self):
        print("Report for solver: %s" % self.solution.solver)

        self.report_summary()
        self.report_conflicts()

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

    def report_conflicts(self):
        tracks = self.solution.tracks

        last_track_multiple_overlaps = False
        for track_name in sorted(tracks.keys(),
                                 key=lambda tn: tracks[tn].total_overlap,
                                 reverse=True):
            track = tracks[track_name]
            if track.total_overlap == 0:
                break

            last_track_multiple_overlaps = \
                self.report_track_conflicts(track,
                                            last_track_multiple_overlaps)

    def report_track_conflicts(self, track, last_track_multiple_overlaps):
        overlaps = track.overlaps

        if len(overlaps) == 1:
            if last_track_multiple_overlaps:
                print()
            other_track_name, num_slots = list(overlaps.items())[0]
            print("%s conflicts with %d slots from %s" %
                  (track.name, num_slots, other_track_name))
            return False
        else:
            print("\n%s conflicts with %d slots from other sessions:" %
                  (track.name, track.total_overlap))

            for other_track_name in sorted(overlaps.keys(),
                                           key=lambda otn: overlaps[otn],
                                           reverse=True):
                print("    %d  %s" %
                      (overlaps[other_track_name], other_track_name))
            return True
