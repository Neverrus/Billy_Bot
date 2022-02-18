from bot import sp


class Spotify:
    def getTrackID(self, track):
        track = sp.track(track)
        return track["id"]

    def getPlaylistTrackIDs(self, playlist_id):
        ids = []
        playlist = sp.playlist(playlist_id)
        for item in playlist["tracks"]["items"]:
            track = item["track"]
            ids.append(track["id"])
        return ids

    def getAlbum(self, album_id):
        album = sp.album_tracks(album_id)
        ids = []
        for item in album["items"]:
            ids.append(item["id"])
        return ids

    def getTrackFeatures(self, id):
        meta = sp.track(id)
        features = sp.audio_features(id)
        name = meta["name"]
        album = meta["album"]["name"]
        artist = meta["album"]["artists"][0]["name"]
        release_date = meta["album"]["release_date"]
        length = meta["duration_ms"]
        popularity = meta["popularity"]
        return f"{artist} - {album}"

    def getalbumID(self, id):
        return sp.album(id)
