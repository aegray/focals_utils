Current State of the world / updated writeup - the top two sections are a description of the steps
i took and the things I found out along the way, the next two sections give you an overview
of what works + what's left, then finally a section laying out the partitions, filesystem and 
apps:



* On the phone app side, almost everything is figured out:

    * Most was learned by digging through the apk - including bluetooth message formats, what
    messages are expected, etc

    * A lot of the glasses features use the android app as a network proxy - sending a 
    bluetooth message to open a socket, a message to send data, etc.  For these services, more 
    was required to get access

    * For most cloud interfaces, after I got access to the device (see below), I was able to override
    the root certificates used on the device for ssl/https traffic, route dns through a local 
    linux box and remap cloud servers to point at a local server, then wrote a small server to 
    accept connections, connect to the real cloud service, and log all decrypted traffic.

        * This gave me capture logs for most of the enabled cloud services used by the glasses

        * Unfortunately there are some services (sports scores, flight info, slack) that were no 
        longer working once I had this ability (for sports and flights it looks like North 
        let it's developer key expire, for the latter, I didn't have an account to try it with)

    * After this, it was decently simple to build a small webserver into a phone app and 
    intercept all network traffic, providing my own responses when necessary.  
    
    * This works for almost all connections on the device (including alexa/amazon), however it 
    does not seem to work for google cloud text to speech, which I'm guessing uses certificate 
    pinning to ensure people like me don't do this.  This is still an open issue - as most 
    text to speech is driven by this service - I'm guessing that we'll have to modify one or 
    more binaries to put in a new api key on the device
 
    * This still required being able to overwrite parts of the filesystem to install a root ca.  
    I eventually realized there was a bluetooth message that let you set the cloud host for most 
    services, bought a cheap domain name (ofocals.com), and got an ssl certificate 
    issued for this domain.  This lets me intercept + decrypt all traffic destined for North's 
    cloud service.  

    * Outside of those issues, most everything else is just a matter of implementation.


* On the glasses side (this is mainly listing out what i've tried / struggled with and the 
    steps to figure stuff out, but if you just want "current state" skip to the next section):
    
    * There is a 4 pin magnetic connector on the glasses, of which only 2 pins are used for 
    charging.  This seemed most likely to be usb, however I ended up spending a lot of time
    analyzing other options when usb wouldn't seem to connect (looked at uart, arm serial debug).
    After looking at it with a logic analyzer I was pretty sure it was usb and I just wasn't 
    connecting well.  Eventually I found a part and built an actual magnetic connector, and 
    after a lot more struggling, finally got it to show up as a usb device

    * Once the glasses were connected, it shows up as an android device.  adb generally provides
    device access and debugging commands, however when you run the command "adb devices", the 
    glasses would show up as "unauthorized" - which generally means that you need a private key
    to match a public key on the device.  

    * Most android phones and watches have some sort of key sequence or menu where you can enable
    adb debugging, i tried for a while to find something on these but didn't find anything.

    * After trying to connect to the glasses through usb when they were turned off, they showed
    up as a different device - a qualcomm based device.  When I read more about this, I found
    out a lot of qualcomm chips have several different modes, and they can be triggered in 
    different ways - sometimes by driving or grounding a pin, sometimes by grounding one of the 
    usb wires.  After this I figured out that you can ground D- before plugging in the usb cable,
    plug in, then unshort D-, and it brings up a special mode in the chip called EDL 
    (emergency download mode).  

    * I read a decent amount about this and found a repo that has utilties for talking to this 
    mode, however there appears to be a base/starting mode that is used for basic device 
    identification and upload of a secondary loader.   To make real use of this, you have to 
    upload a "firehose programmer" which is a small program that speaks another protocol, but
    lets you read/write from the filesystem and memory of the device (including memory mapped
    parts of the chip like fuses).  

    * In some of the prints from the edl program I used, it displays the devices public key hash, 
    but has the additional statement:
            "Unfused device detected, so any loader should be fine..."

    * I found a several collections of firehose programmers on the web, and eventually found 
    one that worked.  This gave me access to both read + write the filesystem of the device
    (however I could only practically overwrite - adding files or changing file size was 
     not easy)

    * I tried adding my adb keys to several locations in roundabout ways (required 
        overwriting some parts of one file with my keys, and overwriting parts of 
        an init script to read from that file and write to my destination file), however
        this did not seem to work.

    * After a bit more research, qualcomm has "qfuses" in their chip, that can be blown one 
    time to set some flags in the processor.  This is generally how an oem would enable 
    secure boot - which would cryptographically sign each level of bootloader running on the 
    device.  I ended up confirming that these were not set, and the device was safe to install
    a new kernel/boot partition to.  
        
    * Eventually got the courage to unpack the boot partition, add adb keys there and edit 
    android's default.prop to enable debugging, root, and some other things normally done to 
    root a device.  However, when I wrote this to the glasses, I was completely locked out.  The
    glasses would now only boot to fastboot (android's restore utility), and when I ran some 
    commands through fastboot, it revealed that there was a tamper flag set, which I had triggered.

    * Someone else from the focals subreddit let me borrow theirs, and I worked with those until
    I finally figured out how to fix the tamper flag 

    * Figured this out very recently: For root + tamper flag, apparently it stores all this info 
    in the devinfo partition on the emmc.  Because we have write access here, it's trivial to 
    overwrite it with your own flags + reenable the device (this took a long time to figure out)

    * Still had no adb access, so the device was still relatively locked

    * Finally, after digging through strings from various apps, I found that the copy of 
    adb they have in the boot partition was missing strings which would refer to standard locations
    of adb keys, and they had strings for both /system/etc/ssh/mfg_keys and somewhere else in the 
    /thalmic partition

    * I used edl to read the /system partition, grepped to find the byte offset of the mfg_keys
    file, then wrote my own pubkey over the key at that offset.  This gave full adb access
    (with root as default strangely)

    * Past there, I figured out some through reverse engineering apps with ghidra:
    
        * Most of their framework is QT based 
        
        * Network connections are not done through the normal linux stack - there is a 
        library called "csl" that the base QT network library has been modified to use.
        This takes makes socket connections communicate by sending a standardized set of
        bluetooth messages through the phone app, and the phone handles the actual socket
        connections.  /system/bin/csl_test is a test app that shows how this works, and I 
        initially made progress on this by reversing that app

        * I reversed /system/bin/demo_notes and drew up some basic psuedocode for it - using 
        this as a skeleton, I worked out what library calls were non standard and would be 
        needed - mostly in:
            /system/lib/libblack_coral_style.so
            /system/lib/libblack_coral_app.so

        * I got together a cross compiling toolchain (see glasses/toolchain_setup.txt) and 
        hacked together a build of the same version of qt that was on the glasses

        * Finally, worked out the headers needed to build against these libs, and after a 
        decent amount of tweaking, got my mocked up app to compile + run - this provided a new
        lens / slide on the main glasses display.

        * Most of the apps are qml based (QT's markup language) - the apps often just wrap 
        loading some qml resources that are compiled into the binary.

* Summary of what's done:
    
    * Most of the android app - there are still features to be implemented but I have an app
    i'll probably push that replaces a lot of what the original app did, with some plugins to add
    your own content to certain parts of the glasses (speaker notes, tasks, notes viewer), and 
    adds phone music controls

        * this includes "cloud mock" which serves up fake cloud services in place of the 
        previous real cloud services

    * Adb access / root on the device

    * I can build a basic application / "lens" that displays as one of the slides you see in the 
    glasses.  This gives the basics of displaying + custom apps
    
    * Network io done through qt libraries automatically works through the phone, which 
    gives a packet stream both to the phone and out to external servers

    * I have a basic app for the glasses that periodically tries to open a network connection to 
    the phone app, then, when connected, checks for a list of apps, downloads qml code for each,
    and opens a lens/slide to show each app in the gallery
        
        * Currently I've added the game 2048 to the glasses that I found qml source for 
        somewhere online, but it's trivial to write more apps


    * The protocol that the peripheral ring / input device speaks has been reverse engineered in 
        case anyone wants to build a replacement app or device - see loop/

* What's left:
        
    * Most of the api/libs on the glasses are still unknown:

        * there are a lot of components available to qml apps in libblack_coral_style.so and 
        libblack_coral_app.so that I haven't figured out how to use.  There's a script in 
        glasses/tools/ that can be used to read some portions of compiled qml from binaries,
        but outside of that, that's all the further I've gone
        
        * I haven't dug into how bluetooth messages get received or sent - I have code 
        to open network connections, but this generally requires the glasses to initiate the 
        connections.  It would be nice to be able to receive bluetooth messages on the glasses
        and handle them, rather than periodically trying to connect out

        * Along the same lines - there is clearly a way to register for events like 
        "screen woke up", "phone connected", etc. Because I see applications sending messages
        and network traffic when this happens, but I haven't looked into how this works yet

        * There is some way to register "experiences"  which are programs that are launchable 
        through a bluetooth message from the phone - I have not looked into the api for this,
        although I assume its decently trivial

        * Audio - I know there is some way to access the microphone and play sound through the 
        speaker because the alexa app on the glasses does this, but I haven't dug in enough
        to figure out how.

        * Video - it looks like the default qtmultimedia plugin for qml is either not 
        set up correctly, or I'm doing something wrong.  It would be cool to figure out 
        if we can play video on the glasses

        * There is an app called "monocular" which I've been trying to figure out for a long 
        time - based on different parts of the code I've reversed, it looks like it connects
        out to a server, opens a websocket, publishes a json message specifying width, height, 
        and framerate, then waits for image data in some format on the screen - my guess is that
        this is effectively a "remote viewer" that you can just stream image data to,
        however everything I've tried here doesn't seem to work.

            * As a commplement to this, they have another app called "konacast" which does the
            opposite - it connects out to a server and sends image data repeatedly for what
            is on the screen of the glasses.  I have a primitive app that displays this output
            (see glasses/tools/konacast_display.py)

            * I'm hoping if we figured out exactly what format it's expecting, it would 
            give us a way to launch an app and display arbitrary content on the fly without 
            requiring modifying anything on the device (as building a connector cable is p
            probalby out of reach of a lot of people)


        * I see references both to bnep (bluetooth network) and wifi - which I assume means there is some 
        other form of networking that could be enabled on the device.  When I tried enabling 
        the bnep stuff, it resulted in some sort of segfault or unkonwn ioctl - which either 
        means I'm doing something wrong or it doesn't actually work on this device

            * There are also ssh keys on the device in /system/etc/ssl - which to me says
            there is some way to ssh to the glasses

        * There is a protocol "garnet" referenced in a bunch of places - which I've inferred is 
        some sort of display through usb used for debugging.  That's all I know, but this could be 
        interesting

        * There are some things like the "quick action" menu that pop up if you click and 
        hold the ring /loop device - i'd like to figure out how to add actions here

    * The biggest question: is there any way to add software without having to build 
    a connector cable, fight with edl, etc.  Ideally we would have something software based
    that would make it easy for anyone to get custom software onto the glasses

        * North would add and remove software with a standard android OTA update - which is 
        generally a zip file that contains mostly binary patches, and the content is signed 
        with North's release keys.  
        
            * I have copies of the last 2 ota packages, but I have not tried pushing my own 
            update package to see what happens if you don't sign things correctly.  
            
            * Additionally, I don't know enough about the ota update process to know if there 
            are any ways around the signing, or what happens if you push a package with a bad 
            signature.

            * If we figured this out, it would be trivial to add custom software - as I have a 
            decent understanding of the update process from the phone side already (how it 
            transfers files and notifies that there is an update available)

        * Encryption?  If they sign their updates, I assume that means the public keys are stored
        on the system and the private keys are not.  However, I have not dug into this much - 
        there are several places on the chip or emmc where encryption keys could be stored.  I'm 
        not sure if this is worth digging into or not

        * Exploits?  I've messed around a lot with format strings, overflows, etc.  However
        once I got more into reversing - it looks like there are stack canaries used throughout 
        the code (I'm not sure about if ASLR is enabled, but I assume it is), which would make 
        exploiting this way more difficult.

            * There are some commands that, when received by the glasses, will cause the glasses
            to attempt to transfer a file from the phone to the glasses filesystem (mainly 
                notifications that say they have an icon and the message saying an update is 
                available).  I've messed with transfering arbitrary files through the notifications
                and can get something like a wav file transferred, however in all my experiments
                it looks like it does an ok job of escaping the filenames I send and all files
                end up in the same data directory.  I had been thinking maybe there was some 
                way to provide a correpted filename and get it to write somewhere else in the 
                filesystem, but even if I can do that, it still leaves the question of "how do 
                I trick it to execute code that wasn't there before


            * Another complication - the /system partition is generally mounted read only 
                (at least when connecting through adb shell), so I assume that means we can't 
                write to it 

                * However, it's entirely possible if we could get arbitrary code to run, we
                could read directly from the mmc rather than the filesystem, figure out some 
                offset in an existing file, then overwrite some portion of that file
                
            
* Partition layout and filesystem layout:

     I *think* there is one emmc device hooked up to the chip, which is where all the data 
     is stored.  It's entirely possible I'm wrong about this - I have not dug enough into the 
     hardware side of things.  The partition table is relatively standard for android:

     (see https://source.android.com/devices/bootloader/partitions-images)


    /sbl1 (sbl1bak is backup i think) - secondary bootloader


    /aboot (abootbak is backup i think) - android bootloader I think - does initial loading of 
        android kernel 

    /rpm (rpmbak) - not sure
    /tz (tzbak) - trust zone partition - i think storing encryption keys?

    /modem - 
    /modemst1 -
    /modemst2 - no clue - I assume related to if the chip is used in a phone

    /misc - holds data written for the bootloader to use as flags for recovery

    /fsc - no clue

    /ssd - no clue

    /splash - no clue - i assume an image if the device booted in a normal fashion

    /DDR - no clue

    /fsg - no clue

    /sec - security partition?  not sure

    /boot - holds android kernel image + ramdisk.  

    /system - holds system config, binaries, and libs 

    /persist - not sure 

    /cache - used for recovery + ota updates

    /recovery - i think holds a backup for when updating

    /devinfo - device info - holds a struct on disk that has flags for "is_root, is device tampered, etc"
        for further info - you'd have to look into the android bootloader (aboot) code online, 
        although this appears to be a custom build so I couldn't find direct source for it

    /cmnlib (cmnlibbak) - not a clue

    /keymaster (keymasterbak) - i assume encryption related but may be unused

    /keystore - same, maybe encyption related but may not be used

    /oem - oem data, but this appears empty

    /config - not sure

    /userdata - data storage / logs, etc

    /thalmic - extra partition with files specific to their hardware / projector - appears to have
        projector calibration data of some sort


* binaries (/system/bin):

    There are many more - thes are only the ones I have some idea of what they are:
    
    * alexa_app - i think provides the view / controls over alexa (receive voice input, 
            send + get network response, possibly playback media)

    * alexa_service - i assume supporting service for the alexa_app

    * balloons - demo "experience" that shows some balloons, takes input from the loop, and 
        animates popping them

    * black_coral_simulator - appears to be an app that acts as a simulator for the on glasses
        system and allows sending bluetooth messages to mock up certain scenarios for testing
        -> may be worth reversing to understand the bluetooth data path

    * csl_test - tests qt based networking through the phone

    * csl_service - i assume a service supporting the csl networking lib

    * daily_briefing - related to alexa providing a daily media file telling you the latest news

    * demo_notes + demo_tasks - demo applications demonstrating showing a list of notes or tasks
        with fixed data

    * feature_manager - i think related to enabling or disabling apps on the glasses based on 
        input both from the cloud and from the phone app

    * explore_app + explore_service - App + service related to showing local location information/
        cards telling you whats around

    * jukebox_app - connects to the cloud to get the status of your spotify, if its playing, shows
        an extra card on the main glasses screen showing info about the song + letting you 
        control it.  This might be useful to reverse engineer to learn how to add 
        a card or info to the main screen of the glasses

    * kona_media_player - experience which takes a file argument and plays it - I only ever got
        this to work with a wav file

    * konacast - experience that, when launched, tries to connect out to a host provided as an 
        argument and streams screenshots to provide a remote view of the glasses screen

    * launcher_lens_app - an app that can launch a different, fixed set of apps.  I got this to 
        show up, but it would never launch anything, so I'm not sure if this is just something 
        left over from an old version of their software

    * notes_app - shows a lens/slide, connects to cloud and downloads notes from a cloud service
        to display on your screen (generally linked with onenote, evernote, or pushbullet)

    * monocular - I think related to displaying images streamed from a remote server, however
        I never figured out the format 

    * music_id_app - listens to the microphone, broadcasts an audio "fingerprint" to a cloud 
        service to see if there is a matching song.  In order for me to replicate this, 
        we'd have to reverse the "fingerprint" to understand what service they're using in the 
        backend (I assume its a shazam api)

    * notification_app / notification_serivce - related to the lens/slide that displays notifications
    from the phone.  It would be useful to reverse this to see how they make a pop up happen
    no matter where you are on the glasses

    * sky_caption - supposed to display flight info - i never got it to work

    * social_app - i think related to displaying threads for various social apps like twitter

    * tasks_app - shows tasks which are grabbed from the cloud - usually linked with an 
        external service like todoist

    * telepath_lens_app + telepath_service - related to display sms messages + conversation threads

    * teleprompter - connects to a web service they have and speaks a simple websocket json protocol
        to display slide notes for a powerpoint like / google presentation.  In the phone app
        I have a web endpoint overridding their webapp to provide custom content through this
        (was using it to control+display anki flashcards, but also have live subtitles using 
         google cloud speech, and an example of streaming text to the display)

* libs: (/system/libs) - only the ones I think are critical and know what they are:

    * libblack_coral_app.so - provides core functions and classes related to appliations they 
        run - for example a class that knows how to display a lens on the screen / in the 
        slide gallery

    * libblack_coral_style.so - I think provides components that are custom to the glasses available
        for use from qml.  There is a lot in here that I haven't explored

    * libcslclient.so - provides network connectivity through their bluetooth based transport
        (there is also a libcslserver.so - does that mean we could run a server??)

    * libgoogleapis.so - I assume related to google cloud speech - maybe this has their api 
        key + is where we could put in our own to reenable speech to text?

    * libQt* - qt libraries - some have clearly been built with custom code in them

    * libthalmic* - not sure but they are from this company (used to be named Thalmic) - so 
        I assume there is something useful in here







    












