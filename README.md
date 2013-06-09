<h1>Swisher</h1>

<ul>
  <li>Swisher is a fun way to play music at home</li>
  <li>You associate songs with physical cards and then wave them past a pad to play the song</li>
  <li>There is a demonstration video <a href="http://youtu.be/6y7gLkIasRE">here</a> (you might need to turn up your volume)</li>
  <li>To use it you need a 'driverless USB RFID 125khz reader' and some 125khz RFID cards</li>
  <li>It costs about £20 ($30) in total for a reader and 30 cards
   (postage can be quite slow and the price for the cards is very variable)</li>
</ul>

<img src="https://raw.github.com/thomasrynne/jamendo-contest/master/swisher/assets/whiteboard.jpg" width="300em" style="border: solid 2px black; margin-left: 1em; margin-right: 3em; float: left"/>
<img src="https://raw.github.com/thomasrynne/jamendo-contest/master/swisher/assets/rfid-reader.jpg" width="150em" style="border: solid 2px black; margin-left: 1em; margin-right: 1em; float: right"/>

<p>There are two versions. <a href="http://swisher.herokuapp.com">Swisher-Web</a> and Swisher-Box which you install</p>
<div>
 <div style="float: left; margin-left: 4em; border: solid 1px black; width: 20em; padding: 5px">
   <h3>Swisher-Box</h3>
    <ul>
     <li>Runs on Linux (including a <a href="http://en.wikipedia.org/wiki/Raspberry_Pi">Raspberry Pi</a>)</li>
     <li>You need to install Mpd/Mopidy and Swisher</li>
     <li>Plays your mp3s and Jamendo tracks/albums/radio</li>
     <li>Cards always work</li>
    </ul>
 </div>

 <div style="float: right; margin-right: 4em; border: solid 1px black; width: 20em; padding: 5px">
   <h3>Swisher-Web</h3>
    <ul>
     <li>Runs on anything with a modern browser and a usb port</li>
     <li>No installation required</li>
     <li>Only plays Jamendo tracks/albums/radio</li>
     <li>Cards only work when a 'swisher.herokuapp.com' page is at the front and has focus</li>
    </ul>
 </div>

 <div style="clear: both"></div>

<h1>Swisher-Box</h1>

Here are the instructions on installing swisher-box.

 Hardware Requirements
---------------------
- An RFID card reader (described above)
- You also need a PC and speakers
- It was created with a [Raspberry Pi](http://www.raspberrypi.org) in mind but any Linux PC will do

Software Dependencies
---------------------
- MPD/Mopidy - Swisher-Box is an [mpd](http://mpd.wikia.com) client so you need a working mpd installation first. It also works with [Mopidy](http://www.mopidy.com/) an alternative mpd server which plays music from multiple sources.
- evdev - a linux kernel module which is usually already present
   (check you have the directory /dev/input and read permissions)

Installing
----------
    > sudo apt-get install python-dev python-setuptools
    > git clone https://github.com/thomasrynne/swisher.git
    > cd swisher
    > python setup.py install
    > swisher

 Go to http://localhost:3344 with a browser and you should see the swisher web page

Using
-----
 The swisher webpage lets you search for tracks and albums and lists some radio stations. Search for a song and press play first to check that playing is working.
 
 To associate cards with songs you press the zigzag button of the song and then
 swipe the card. After that swiping the card should play the song.

 As well as songs, 'actions' can be associated with cards so you can make
 cards for stop/next/previous... See the /Actions page

The Cards
---------
 There are many ways to use the physical cards. Here are some suggestions:

- Stack of cards with song names written on sticky labels on the card
- Stick pictures on the cards (for example album covers)
- Put magnets on the card and keep the cards on a fridge or magnetic whiteboard
 - You can also bend the end of the cards in very hot water 
    which makes it easier to take them of the whiteboard
 - Magnets intended for shower doors are cheap and the right strength
- Cut round the antenna to make the cards smaller and stick them to toys
 - Hold the card against a bright light to see where the antenna is
 - Don't cut off the RFID chip which is usually a dot just outside the
   round antenna

- You can also get keyring RFID tags. I have not tried these yet.

Please experiment yourself and let me know what works.

Optional  Configuration
-----------------------

### Jamendo

 [Jamendo](http://www.jamendo.com) hosts free music for personal use.
 If you set the values jamendo-username: [username] and jamendo-clientid: [clientid] in the configuration file the following pages are added: 

- Jamendo Search: lets you search jamendo tracks and albums by title
- Jamendo Radio: lists the Jamendo radio stations
- Jamendo Likes: lists your favourite and liked tracks

Using these pages you can associate Jamendo tracks,albums and radio stations with cards. Here is a screenshot of the radios page:

![Screenshot of jamendo radio page](https://raw.github.com/thomasrynne/jamendo-contest/master/screenshots/jamendo-radio.png)

### Specify the reader

 Driverless RFID readers behave like a usb keyboard and simulate typing
 in the card number when a card is waved as if it was entered through a keyboard.
 This means numbers get entered in the active terminal.

 If you want to suppress this you can tell swisher which
 device is the rfid reader and it will grab and suppress the fake
 key presses.

 Run "swisher --list-devices" before and after plugging in the USB RFID reader
 to see the name of your RFID reader. Then use 
  the --grab-device argument or specify grab-device: 'name' in /etc/swisher.conf
  if you are using the init script (see below)

 By default swisher connects to mpd on localhost 6600
 You can change this with the mpd-host and mpd-port properties
 
 By default the swisher web server listens on 3344
 You can change this with the http-port property

### Start on Boot

    > sudo cp misc/init.d.swisher /etc/init.d/swisher
    > sudo cp misc/swisher.conf /etc
    > sudo update-rc.d swisher defaults

