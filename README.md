# py-sound-scapes

Simple implementation of soundscape generation combining tracks depending on time of day.

Selects tracks depending on time of day, tracks should be sorted into the provided folders, a couple of examples extracted from freesound.org are provided.

Streams added wav tracks in an infinite loop to HTTP address, signal can be retrieved with programs like VLC.

HTTP stream uses continuous buffer send, as in https://stackoverflow.com/questions/59065564/http-realtime-audio-streaming-server