#!/usr/bin/env python

import csv
import re

from openstack_schedules.track import Track


class TrackCollection(dict):
    def __getitem__(self, track_name):
        if track_name not in self:
            self[track_name] = Track(track_name)
        return super().get(track_name)

    REQUIRED_CSV_FIELDS = ['TRACK', 'MIN_LENGTH', 'MAX_LENGTH', 'CONFLICTS']

    @classmethod
    def from_csv(cls, csv_path):
        tracks = cls()

        with open(csv_path, 'r') as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for required_field in cls.REQUIRED_CSV_FIELDS:
                if required_field not in csvreader.fieldnames:
                    raise(RuntimeError("%s field missing from %s" %
                                       (required_field, csv_path)))

            for row in csvreader:
                track_name = row['TRACK'].strip().replace('/', ' ')
                conflicts = re.split(',\s*', row['CONFLICTS'].strip())
                conflicts = list(filter(None, conflicts))
                tracks[track_name] = {
                    'min': num_field(row['MIN_LENGTH']),
                    'max': num_field(row['MAX_LENGTH']),
                    'conflicts': conflicts
                }

        return tracks


def num_field(val):
    if val is None:
        return None

    val = val.strip()

    if val == "":
        return None

    return int(val)
