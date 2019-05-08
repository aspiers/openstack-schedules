#!/usr/bin/python

import re

from openstack_schedules.utils import abort
from openstack_schedules.track import Track
from openstack_schedules.track_collection import TrackCollection


class Solution(object):
    def __init__(self, solver):
        self.solver = solver

        # solution's value of objective function
        self.objective = None

        self.tracks = TrackCollection()

    def start_track(self, track_name, slot):
        self.tracks[track_name].start = slot

    def end_track(self, track_name, slot):
        self.tracks[track_name].end = slot

    def overlap(self, track1_name, track2_name, overlap):
        self.tracks[track1_name].overlap[track2_name] = overlap

    def cbc_name_to_human(self, track_name):
        return track_name.replace('~', '-').replace('_', ' ')

    def parse_cbc(self, solution_file):
        for line in solution_file.readlines():
            if 'nfeasible' in line:
                abort(line)

            m = re.match("^Stopped on (?:time|iterations) - "
                         "objective value -(\d+\.\d+)$", line)
            if m:
                self.objective = int(float(m.group(1)))
                continue

            m = re.match("^Optimal - objective value -(\d+\.\d+)$", line)
            if m:
                self.objective = int(float(m.group(1)))
                continue

            m = re.match("^\s*\d+\s+track_start\('?(.+?)'?\)\s+(\d+)", line)
            if m:
                track_name, slot = m.groups()
                track_name = self.cbc_name_to_human(track_name)
                self.start_track(track_name, int(slot))
                continue

            m = re.match("^\s*\d+\s+track_end\('?(.+?)'?\)\s+(\d+)", line)
            if m:
                track_name, slot = m.groups()
                track_name = self.cbc_name_to_human(track_name)
                self.end_track(track_name, int(slot))
                continue

            m = re.match("^\s*\d+\s+overlap\('?(.+?)'?,'?(.+?)'?\)\s+(\d+)", line)
            if m:
                track1_name,  track2_name, overlap = m.groups()
                track1_name = self.cbc_name_to_human(track1_name)
                track2_name = self.cbc_name_to_human(track2_name)
                self.overlap(track1_name, track2_name, int(overlap))
                continue

    def report(self):
        print("Report for solver: %s" % self.solver)

        self.report_summary()

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

    def report_summary(self):
        for track_name in sorted(self.tracks.keys()):
            track = self.tracks[track_name]
            print("%-25s  %d %s  length %d  |%s|" %
                  (track_name,
                   track.start,
                   "to %d" % track.end if track.end > track.start else "    ",
                   track.length(),
                   self.pic(track)))
