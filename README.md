# focals_utils


This is a code+info dump of a side project I was working on for focals.  All the code runs
locally, but I haven't had time to clean things up / package it in a way that would be generally
usable.

Organization (or lack thereof):
* android_apps/bluetooth_test2/ is an example android app that replaces the default 
    focals app, and can connect to the glasses and provide an intercept for the presentation 
    projector to serve several different example/hacky test features:
    * Anki flash card serving (left click = failed, right click = pass)
        - this was my main daily use of this app 
    * Streaming text (as a demonstration of an ebook reader I was going to write for the glasses)
    * Live subtitles (depends on how good your microphone and network connection are) - listens
        with the phone's speaker microphone and uses google cloud text to speech to stream 
        subtitles of any spoken words to be displayed on the glasses.   This works well enough 
        in quiet settings, but has an issue if the network ever lags.  

    Additionally it has some example code for doing some things like generating notifications
    on the glasses

    Note that because this controls the bluetooth connection to the glasses, it requires that you 
    first disconnect from the main application.  Additionally, most features won't be available
    when connected to this app (although I think it would be possible to recreate relatively 
    easily).

* btmsgprotos - This contains protobuf definitions of the bluetooth messages for each software
    version, and diffs between the versions to see what got added
    
* connector - This has notes on building a data connector, and some notes on actually 
    communicating that's built, downloading firmware etc.
   
* info - this just has a snapshot of fcc filings in case any useful information is in there

* linuxtools:
    * failures - random experiments I tried:
        * serve_lensecast.py -> one experience available on the focals app is "lensecast", where
            the glasses connect to a webserver, open a websocket, and then periodically send
            image data representing what you see on the screen.  This script just acts as that 
            webserver and writes all data to output.txt to examine

        * serve_monocular.py -> one experience is called "monocular" - my guess is that this
            connects to a webserver, opens a websocket, then waits for image data to display 
            on the glasses.  However I could never figure out the format to send, so this never
            went anywhere

        * serve_websocket.py / serve_websocket_bin.py -> these were random attempts for 
            figuring out monocular - they just serve a websocket on some port and 
            once connected, feed the data out of output.txt to the glasses


    * pycompanion - python program and related tools to act as the focals phone application and 
        provide various debugging tools for testing.  If the glasses are not connected to the 
        phone, they will connect to this instead and think they are connected to the phone app.  

        This is horrendously written + hacked together - in order to support separate 
        "services" that i could load and unload on the fly without having to break the connection
        to the glasses by killing the main app, it publishes all messages received on a 
        udp connection and forwards any messages received on another udp connection as a 
        bluetooth message to the glasses.

        The main app is connect.py and acts as a command line - the following commands are valid:

            * pair - tell the glasses to pair with the loop device

            * exp <name> [key=value ...] - Start an experience with the given arguments.
                Examples:
                    exp Balloons
                    exp "Media Player" filePath=/data/kmp
            * sexp <name> - Stop an experience that was previously started

            * conn {0,1} - Tell the glasses if the network is connected (example: conn 0)
                - this is used with the service_network.py app - which acts as a socket manager
                to facilitate the glasses communicating with the internet.

                Unfortunately this only semi worked - I never dug in enough to see why 
                it sometimes failed

            * dummy n - where n is an integer.  There were a number of bluetooth/protobuf message 
                ids that I didn't find in the android app - this is a command to send an 
                empty message with id=n to see if it triggered anything on the glasses.
                This never resulted in anything

            * tsettings - request the glasses to send back a message describing all templated 
                settings which it has.  These are printed to the screen once received

            * features - request the glasses send a message describing all available features.
                This is printed to the screen once received.

            * caplogs [name] [reportId=xxx] - Capture logs with an optional report id.  I 
                never really figured out what this does, but I think it tells the glasses to 
                start capturing logs

            * screenshot [format] - Capture a screenshot of whatever is on the glasses - it 
                will then get sent back in a message and printed to the screen (this is 
                semi useless to just print, but I was seeing if there was any sort of issues 
                with input handling of the format string.  
                
               After I ended up digging through the firmware, it turns out (i think) every 
               app uses stack canaries (not sure if ASLR too) - so this may be pointless
                
    
        Additionally, send_msg.py has lots of examples of things I've tried sending to the 
            glasses to try to trigger behavior.  

        One interesting thing you can do, which I never figured out how to exploit, is 
            you can send a notification with a file id reference - and the glasses will then 
            request to download a file from the main application.  With service_file_transfer.py,
            I was able to transfer a file to the glasses - and it seems that I could get away 
            with non image formats (in my example, a wav file).  

    * update_tools - various one of scripts for exploring update packages.  These are generally
        zip files that are standard android/aosp ota updates, and the majority of the files are 
        binary patches.  

    * findglasses.py - an example of using bluetooth in python to find the glasses, 
        print available services, and other attempts I made like connecting to the main focals
        service

    * projector_webserver_example.py - this acts as a websocket server for the focals projector/
        presentation app.  When used with the android app, you can redirect non https network calls
        to point at your own address - so this was an initial proof of concept.  My goal here 
        was to not have to connect to an external website in order to serve data to my glasses,
        and served as the base for what I would later embed in the android app in order to 
        make my flash cards work.

    * raw_XXX_server.py - raw http server that emulates a websocket server without using 
        a python library.  This was done in order to inspect full headers and raw data that was 
        coming from the glasses

* loop - scripts related to reversing the loop protocol and providing a replacement
    * loop/loop_input.py - this script just connected to the loop device and printed out 
        the raw data it received on any keypresses.  A lot of raw messages are documented in the 
        comments and explain the protocol

    * loop/loop_provider.py - this linux app provides a bluetooth gatt service which will
        emulate a loop device.  If you trigger input pairing when this is running, the glasses
        will connect to it and think it's a loop device.  The app then sits waiting for 
        key presses and forwards them to the glasses as if they were clicks on the loop device.
        Valid keys are: 
            * enter = click
            * arrow keys = directional clicks on the loop

    Additionally, I wrote an android app that attempted to emulate this loop provider script, 
    to have a loop replacement on the phone, however as far as I can tell, the gatt stack
    on android is incredibly buggy - and the glasses would connect to it but then immediately 
    timeout.


Note that anything bluetooth on linux is a massive pain in the ass - and it probably depends 
    heavily on which version of linux, bluez, and gatt you're using.


The most fruitful path I've found to actually running custom software on the glasses will involve
flashing some custom firmware - I have not yet tried this and haven't been messing with 
the glasses recently because I'm so busy with work, but if anyone wants to try, please contact me
and I'll provide directions and possible directions to go


