#!/usr/bin/env python

import csv
import sys

from openstack_schedules.track_collection import TrackCollection


def validate_conflict_tracks(tracks):
    errors = 0
    for track, track_data in tracks.items():
        for conflict in track_data['conflicts']:
            if conflict not in tracks:
                sys.stderr.write(
                    "WARNING: '%s' conflicts with non-existent track '%s'\n" %
                    (track, conflict))
                errors += 1

    if errors:
        sys.exit(1)


def write_tracks_csv(tracks, out_file):
    with open(out_file, 'w') as out:
        writer = csv.writer(out)
        writer.writerow(["TRACK", "MIN_LENGTH", "MAX_LENGTH"])

        for track, track_data in tracks.items():
            if track_data['max'] and track_data['max'] > 0:
                writer.writerow([track, track_data['min'], track_data['max']])


def write_conflicts_csv(tracks, out_file):
    with open(out_file, 'w') as out:
        writer = csv.writer(out)
        writer.writerow(["TRACK1", "TRACK2"])

        for track, track_data in tracks.items():
            for conflict in track_data['conflicts']:
                if tracks[conflict] and \
                   tracks[conflict]['max'] and \
                   tracks[conflict]['max'] > 0:
                    writer.writerow([track, conflict])


def main():
    tracks = TrackCollection.from_csv(sys.argv[1])
    validate_conflict_tracks(tracks)
    write_tracks_csv(tracks, sys.argv[2])
    write_conflicts_csv(tracks, sys.argv[3])


if __name__ == '__main__':
    main()
