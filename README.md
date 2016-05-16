# cmus-notify
#### *GTK script for CMux console media player*

### It does:  
  * send desktop notification about currently playing track;
  * save currently playing track into the favorites playlist;
  * send currently playing track love to last.fm
  
### Dependencies
```
python 2.7
python-gtk2
python-notify
```
Users of xfce4 can also use xfce4-notifyd-config to modify notification bar.  
  
### Installation
```
chmod u+x /path/to/notify-cmus.sh
```
In CMus command line:
```
set status_display_program=/path/to/notify-cmus.sh
```
or call the script from another one, f.e, it could be called from the `last-cmus` scrobbler with:  
```python
from subprocess import call
call(["python", "/path/to/cmus-notify.py"])
```
  
#### User-specific properties
##### set yours system user name
```
user = "username"
```
##### set yours favorites.pls path
```
playlist = "/path/to/favorites.pls"
```
##### create last.fm API account and generate keys
For now, to be able to send track love to last.fm, a specific API account should be generated for embedding the script with personal api and secret keys:  
```
APIKEY    = "apikey"
SECRETKEY = "secretkey"
```
##### choose notification timeout (seconds)
```
timeout = 10
```
  
### Possible issues
Verify an output from `cmus-remote -C`. If there is an error, then try to replace the array  
```python
cmus = ["cmus-remote", "-C"] 
```
in `cmus-notify.py` with an array  
```python
cmus = ["cmus-remote", "--server", socket, "-C"]
```
