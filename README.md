mpd info service
==================
Shows info to the current songname, albumtitle and a cover on a simple
webpage, for example to view the cover in an "Magic Mirror", displayed
on an Raspberrry PI 7 Inch display.


Finds the cover by:

- searching the directory of the song for some default filenames
  (cover.png etc)
- if no cover could be found, executes a shell script. 
- if current song is a stream, looks for a file inside the streams
  directory (all slashes are replaced by pipes, i.e
  http:||example.com|stream.m3u


Screenshot
----------
![example screenshot](screenshots/example.png "Screenshot")

Install
--------
- clone the repo
- install the pythin requirements 
- install systemd unit file: 
   - edit the systemd mpdinfoservice.service
   - copy the mpdinfoservice.service to /etc/systemd/system, 
   - sytstemctl enable and start it

``` shell
cd /srv/
git clone 
cd mpdinfoservice
pip3 install -r requirements.txt
# vi
cp  mpdinfoservice.service  /etc/systemd/system
systemctl enable /etc/systemd/system/mpdinfoservice.service
systemctl start /etc/systemd/system/mpdinfoservice.service
```

Configuration
-----------------
Configuration is done through the following  environment variables:
- MPD_HOST: Host mpd runs on (default localhost)
- LISTEN_ON: IP to listen to. (default 127.0.0.1)
- PORT: port to listen
- MPD_ROOT_DIR: local music directory (default /data/Musik) 


Logs
-----
Logs can be view with 

``` shell
journalctl -u mpdinfoservice.service 
```
