from openstack_schedules.track import Track


class TrackCollection(dict):
    def __getitem__(self, track_name):
        if track_name not in self:
            self[track_name] = Track(track_name)
        return super().get(track_name)
