HelloHyperion for Plex and HyperionWeb
=================

##### Automatically turn on a Hyperion led strip with Plex!

**Credits**
This channel is based on HelloHyperion by ledge74.

### Behavior

This channel detects when a media is playing, paused or stopped on your Plex Clients. Then it checks if it's a video, the client name, and the user who owns the stream. If it matches your criteria it triggers your lights with the actions you have set up.
You can also turn your lights on and off inside the channel.

### Configuration

The config is pretty simple and only needs to be done once. Configure your settings following the details below.
The plugin watches over **one client**, **one or multiple users** and **one led strip** that is connected to HyperionWeb, as well as the actions: on play, on stop, on pause, dim value, and only trigger if it's dark outside.

* ```Activate HelloHyperion``` Untick to deactivate.
* ```Plex.tv login``` is your Plex login.
* ```Plex.tv passwords``` is your Plex password. It is only sent to plex.tv to get an identification token (so you must have a working internet access).
* ```Plex Server Address``` is the local adress to reach your server.
* ```HyperionWeb Address``` is the local address to reach the HyperionWeb server.
* ```Nearest city from your location``` is used to calculate to calculate sunrise/sunset hours at your location.
* ```Name of plex client able to trigger``` You can find the list of users in PMS -> settings -> devices. Only put ONE client!
* ```Name of the users able to trigger``` You can find the list of users in PMS -> settings -> users -> myhome. You can put multiple users (comma separated values, case sensitive).
* ```When a media is playing``` is the action that will fire when a media is playing.
* ```When a media is paused``` is the action that will fire when a media is paused.
* ```When a media is stopped``` is the action that will fire when a media is stopped.
* ```Change value gain``` is the brightness which the led strip will use. (10 is the min brightness and 100 is max)
* ```Do also change brightness when media is played``` uses the value above to set a specific brightness.
* ```Revert back brightness after media has stopped``` reverts brightness when media is done.
* ```Randomize color and saturation on Value Gain/Turn On``` will randomize your led color each time the action turn on or value gain is fired.
* ```Only trigger lights if it's dark outside``` Tick to only trigger your lights between sunrise and sunset.
* ```Preset 1, color (hex): #``` hexadecimal color value for color preset 1 (don't write the #).
* ```Preset 1, brightness:``` brightness value for the led strip.
* ...

### Usage

**How to install:**
* Install the [HyperionWeb](https://github.com/Nosskirneh/hyperionweb) server (a layer over the standard one to keep track of information)
* Go to ```lib/var/Plex/Plex Media Server/Plug-ins/```
* If existing, delete ```HelloHyperion.bundle```
* Run `git clone https://github.com/Nosskirneh/HelloHyperion.bundle
* Unzip the release
* Restart your Plex Media Server
* More indepth: see [article](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) on Plex website.

**On first run:**

1.&nbsp;Configure the channel's preferences (see above for help, make sure that you are connected to the internet as the channel will request a token from plex.tv)
2.&nbsp;Go to the channel (on any device)
3.&nbsp;Enjoy :>

**Use the channel:**

* ```Enable HelloHyperion``` resumes the channel (start listening to items being played)
* ```Disable HelloHyperion``` disable the channel (stop listening to items being played)
* ```Advanced``` --> ```Restart HelloHyperion`` takes into account your new Plex.TV login/password if you updated it in the channel settings.