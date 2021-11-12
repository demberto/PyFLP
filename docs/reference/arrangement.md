## Arrangement

### ::: pyflp.arrangement.arrangement.Arrangement
    selection:
      members:
        - name
        - index
        - playlist
        - timemarkers
        - tracks
        - EventID

## Playlist

### ::: pyflp.arrangement.playlist.Playlist
    selection:
      members:
        - items
        - EventID

## TimeMarker

### ::: pyflp.arrangement.timemarker.TimeMarker
    selection:
      members:
        - denominator
        - name
        - numerator
        - position
        - EventID

## Track

### Event information

Size: 66 (as of FL 20.8.3)

Structure:

| Parameter         | Offset | Type |
| ----------------- | ------ | ---- |
| number            | 0      | I    |
| color             | 4      | i    |
| icon              | 8      | i    |
| enabled           | 12     | bool |
| height            | 13     | f    |
| locked_height     | 17     | f    |
| locked_to_content | 21     | bool |
| motion            | 22     | I    |
| press             | 26     | I    |
| trigger_sync      | 30     | I    |
| queued            | 34     | I    |
| tolerant          | 38     | I    |
| position_sync     | 42     | I    |
| grouped           | 46     | bool |
| locked            | 47     | bool |

### ::: pyflp.arrangement.track.Track
    selection:
      members:
        - color
        - enabled
        - grouped
        - height
        - icon
        - items
        - locked
        - locked_height
        - locked_to_content
        - motion
        - name
        - number
        - positon_sync
        - press
        - tolerant
        - trigger_sync
        - queued
        - EventID
        - Press
        - Motion
        - Sync
