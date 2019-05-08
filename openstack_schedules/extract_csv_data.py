#!/usr/bin/env python

import csv
import sys
import re

def extract_track_data(csv_path):
    tracks = {}
    with open(csv_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for required_field in ['TRACK', 'MIN_LENGTH', 'MAX_LENGTH', 'CONFLICTS']:
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
    tracks = extract_track_data(sys.argv[1])
    validate_conflict_tracks(tracks)
    write_tracks_csv(tracks, sys.argv[2])
    write_conflicts_csv(tracks, sys.argv[3])


if __name__ == '__main__':
    main()
