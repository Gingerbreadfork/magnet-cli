# magnet-cli
Python Torrent Magnet Command Line Client

**Usage:**
1. Install requirements with ```pip install -r requirements.txt```
2. Run ```python3 download.py``` to launch and scan ```magnets.txt``` for magnet links, or alternatively, directly point to a torrent file with the ```-t``` flag or use ```-m``` with a magnet link when launching e.g ```python3 download.py -t awesome_thing.torrent```. You can also include ```-v``` for increased output verbosity.