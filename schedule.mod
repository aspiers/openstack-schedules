# set of schedule slots;
set SLOTS;

param slot_name{SLOTS} symbolic;

table slots_csv IN "CSV" "data/slots.csv":
    SLOTS <- [POSITION],
    slot_name~NAME;
param min_slot := min{slot in SLOTS} slot;
param max_slot := max{slot in SLOTS} slot;
param slot_range := max_slot - min_slot + 1;

# set of tracks
set TRACKS;

# set of pairs of tracks which could potentially cause
# conflicts due to overlap
set CONFLICTS dimen 2 within TRACKS cross TRACKS;

var track_length{TRACKS};
var track_start{TRACKS};
var track_end{TRACKS};
var track_starts_after_slot{TRACKS, SLOTS} binary;
var track_ends_before_slot{TRACKS, SLOTS} binary;
var slot_in_track{SLOTS, TRACKS} binary;
param min_track_length{TRACKS};
param max_track_length{TRACKS};

# The later of two starting slots from a pair of potentially conflicting tracks
var max_start{CONFLICTS};
# The earlier of two ending slots from a pair of potentially conflicting tracks
var min_end{CONFLICTS};
# Temporary booleans for calculating max_start and min_end (see below)
var max_start_bool{CONFLICTS} binary;
var min_end_bool{CONFLICTS} binary;

# Number of slots overlap between a pair of potentially conflicting tracks
var raw_overlap{CONFLICTS};  # Can be negative
var overlap{CONFLICTS};      # Constrained to a minimum of 0
# Temporary boolean for calculating non-negative overlap
var overlap_bool{CONFLICTS} binary;

table tracks_csv IN "CSV" "data/tracks.csv":
    TRACKS <- [TRACK],
    min_track_length~MIN_LENGTH,
    max_track_length~MAX_LENGTH;

table conflicts_csv IN "CSV" "data/conflicts.csv":
    CONFLICTS <- [TRACK1, TRACK2];

minimize satisfaction:
    sum{(track1, track2) in CONFLICTS} overlap[track1, track2];

subject to track_start_constraint{track in TRACKS}:
    track_start[track] >= min_slot;

subject to track_end_constraint{track in TRACKS}:
    track_end[track] <= max_slot;

subject to track_length_constraint{track in TRACKS}:
    min_track_length[track] <= track_length[track] <= max_track_length[track];

subject to track_length_start_end_constraint{track in TRACKS}:
    track_start[track] + track_length[track] - 1 == track_end[track];

# We want to minimise total overlap between conflicting pairs of
# tracks as specified in CONFLICTS.  Overlap between a pair of tracks
# can be calculated via:
#
#   overlap := min(track1_end, track2_end) - max(track1_start, track2_start) + 1
#
# However if they don't overlap, this will be negative, so we actually
# need to calculate max(0, overlap).  (We can't simply specify overlap
# >= 0 as a constraint, because that would prevent the tracks from
# being allowed to have any space in between them.)
#
# max(A, B) can be assigned to a temporary variable C via the
# following four constraints, in which b is a temporary boolean
# variable and M is the maximum possible value of A or B (which in our
# case is the maximum slot index):
#
#   C >= A
#   C >= B
#   C <= A + Mb
#   C <= B + M(1 - b)
#
# This is a cunning trick from:
#
#    https://math.stackexchange.com/questions/2446606/linear-programming-set-a-variable-the-max-between-two-another-variables
#
# The first two constraints are self-explanatory; however they only
# set a lower bound for C, so the last two constraints are used to set
# an upper bound.  They work because if A > B, they can only be
# satisfied if b == 0, in which case the third constraint kicks in,
# ensuring together with C >= A that C == A, and the fourth constraint
# becomes a no-op because B + M will always be greater than A.
# Conversely if B < A, they can only be satisfied if b == 1.

# Assign max_start to max(track1_start, track2_start):
subject to max_start_constraint1{(track1, track2) in CONFLICTS}:
    max_start[track1, track2] >= track_start[track1];

subject to max_start_constraint2{(track1, track2) in CONFLICTS}:
    max_start[track1, track2] >= track_start[track2];

subject to max_start_constraint3{(track1, track2) in CONFLICTS}:
    max_start[track1, track2] <=
        track_start[track1] + max_slot * max_start_bool[track1, track2];

subject to max_start_constraint4{(track1, track2) in CONFLICTS}:
    max_start[track1, track2] <=
        track_start[track2] + max_slot * (1 - max_start_bool[track1, track2]);

# A similar set of constraints can be used to find D == min(A, B),
# where R is the maximum possible range for A and B:
#
#   D <= A
#   D <= B
#   D >= A - Rb
#   D >= B - R(1 - b)

# Assign min_end to min(track1_end, track2_end):
subject to min_end_constraint1{(track1, track2) in CONFLICTS}:
    min_end[track1, track2] <= track_end[track1];

subject to min_end_constraint2{(track1, track2) in CONFLICTS}:
    min_end[track1, track2] <= track_end[track2];

subject to min_end_constraint3{(track1, track2) in CONFLICTS}:
    min_end[track1, track2] >=
        track_end[track1] - min_slot * min_end_bool[track1, track2];

subject to min_end_constraint4{(track1, track2) in CONFLICTS}:
    min_end[track1, track2] >=
        track_end[track2] - min_slot * (1 - min_end_bool[track1, track2]);

# Calculate raw overlap, which could be negative
subject to raw_overlap_constraint{(track1, track2) in CONFLICTS}:
    raw_overlap[track1, track2] =
        min_end[track1, track2] - max_start[track1, track2] + 1;

# Now impose minimum overlap of 0
subject to overlap_constraint1{(track1, track2) in CONFLICTS}:
    overlap[track1, track2] >= raw_overlap[track1, track2];

subject to overlap_constraint2{(track1, track2) in CONFLICTS}:
    overlap[track1, track2] >= 0;

subject to overlap_constraint3{(track1, track2) in CONFLICTS}:
    overlap[track1, track2] <=
        raw_overlap[track1, track2] + slot_range * overlap_bool[track1, track2];

subject to overlap_constraint4{(track1, track2) in CONFLICTS}:
    overlap[track1, track2] <=
        slot_range * (1 - overlap_bool[track1, track2]);

# Ensure that when track_starts_after_slot is 1, track_start > slot
# and when it's 0, the constraint is a no-op.
subject to track_starts_after_slot_constraint{track in TRACKS, slot in SLOTS}:
    track_start[track] >= slot + 1 - max_slot * (1 - track_starts_after_slot[track, slot]);

# Ensure that when track_starts_after_slot is 0, track_start <= slot,
# and when it's 1, the constraint is a no-op.
subject to track_starts_on_before_slot_constraint{track in TRACKS, slot in SLOTS}:
    track_start[track] <= slot + max_slot * track_starts_after_slot[track, slot];

# Ensure that when track_ends_before_slot is 1, track_end < slot,
# and when it's 0, the constraint is a no-op.
subject to track_ends_before_slot_constraint{track in TRACKS, slot in SLOTS}:
    track_end[track] <= slot - 1 + max_slot * (1 - track_ends_before_slot[track, slot]);

# Ensure that when track_ends_before_slot is 0, track_end >= slot
# and when it's 1, the constraint is a no-op.
subject to track_ends_on_after_slot_constraint{track in TRACKS, slot in SLOTS}:
    track_end[track] >= slot - max_slot * track_ends_before_slot[track, slot];

# Take boolean AND of !track_starts_after_slot and
# !track_ends_before_slot to set slot_in_track, using trick from:
#
# https://cs.stackexchange.com/questions/12102/express-boolean-logic-operations-in-zero-one-integer-linear-programming-ilp
#
# If either track_starts_after_slot / track_ends_before_slot are 1,
# then slot_in_track must be 0.
subject to slot_in_track_constraint_1{track in TRACKS, slot in SLOTS}:
    slot_in_track[slot, track] <= (1 - track_starts_after_slot[track, slot]);

subject to slot_in_track_constraint_2{track in TRACKS, slot in SLOTS}:
    slot_in_track[slot, track] <= (1 - track_ends_before_slot[track, slot]);

# If track_starts_after_slot and track_ends_before_slot are both 0,
# then slot_in_track must be 1.
subject to slot_in_track_constraint_3{track in TRACKS, slot in SLOTS}:
    slot_in_track[slot, track] >=
        1 - track_starts_after_slot[track, slot]
          - track_ends_before_slot[track, slot];

solve;

printf "\n\n=================================================\n\n";

printf "Slots range %d from %d to %d\n\n", slot_range, min_slot, max_slot;

printf "Satisfaction per track\n";
printf "----------------------\n\n";
for {track in TRACKS} {
    printf "%-15s %d--%d (length %d)\n",
        track, track_start[track], track_end[track], track_length[track];
}

printf "\n";

for {(track1, track2) in CONFLICTS} {
    printf "Conflict(%s, %s):\n", track1, track2;
    printf "  max_start: %s\n", max_start[track1, track2];
    printf "  max_start_bool: %s\n", max_start_bool[track1, track2];
    printf "  min_end:   %s\n", min_end[track1, track2];
    printf "  min_end_bool:   %s\n", min_end_bool[track1, track2];
    printf "  raw_overlap: %s\n", raw_overlap[track1, track2];
    printf "  overlap_bool: %s\n", overlap_bool[track1, track2];
    printf "  overlap: %s\n", overlap[track1, track2];
}

end;

# Local Variables:
# Mode: gmpl
# gmpl-glpsol-extra-args: "--tmlim 10"
# comment-start: "# "
# End:
