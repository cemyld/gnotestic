# gnotestic
Suggests continuation for a musical piece using statistical methods.


Issues:
-incompatibility between python3 and midi library, have to migrate to a new midi library since pyqt5 requires python3.
-sent an email to Fabian about transitions between different song segments, didn't understand how the code does the transitions between songs
-without preprocessing songs, the segmentation is quite slow, going to have a cache to store segments
-multiple suggestions only happen right now if a certain segment has more than one transition
-segment needs to be already in the input pool
-add a nice little progress bar since we'll need it when there is no preprocessing