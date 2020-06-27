import socket
import BC_pb2 as msgs
import companion_lib as cl
import time
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32

from companion_lib import make
import google.protobuf.pyext.cpp_message as gpb


UDP_IP = "127.0.0.1"
UDP_PORT = 32123

#avail_path = "../../../../../../../../data/bla.wav" #/\0"*12 + "abcd"
avail_path = "/////data/bla.wav" #/\0"*12 + "abcd"

#-> %5C%5C
#"_".join([str(x) for x in range(1002)])
#"../../../../../../system/etc/test9.wav"
#avail_path = "./../../../../../system/etc/test9.wav"
#avail_path = "1234"
#../../../../../../system/etc/test8.wav"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
#def make(c, **kw):
#    m = c()
#    for k, v in kw.items():
#        if isinstance(v, list):
#            getattr(m, k).extend(v)
#        elif isinstance(type(v), gpb.GeneratedProtocolMessageType):
#            getattr(m, k).CopyFrom(v)
#        else:
#            setattr(m, k, v)
#
#    return m
#

def make_param(k, v):
    m = msgs.ParameterEntry()
    m.key = k
    m.value = v
    return m


def sendmsg(m, extra=None):

    return cl.send_to_socket(sock, m, extra=extra)
    #if field is None:
    #    field = type(m).__name__
    #    field = field[0].lower() + field[1:]

    #print(type(m).__name__, "(", m, ")", field)
    #b = msgs.BlackCoral()
    #getattr(b, field).CopyFrom(m)
    #msg = cl.sendMessage(b)

    #onind = 0
    #while onind < len(msg):
    #    endind = min(len(msg), onind+1000)
    #    cur = msg[onind:endind]
    #    onind += 1000
    #    #endind
    #    sock.sendto(cur, (UDP_IP, UDP_PORT))

#sendmsg(msgs.StartInputDevicePairing(), 'startInputDevicePairing')
#


#m = msgs.StartExperience()
#m.name = "Monocular"
#m.name = "Media Player"
#m.parameters.extend([make_param("host", "127.0.0.1%08x%08x%08x%08x"), make_param("port", "12345")]) #12345")])


#sendmsg(make(msgs.StartExperience, name="Media Player", parameters=[make_param("filePath", "/system/etc/")]))
#sendmsg(make(msgs.StopExperience, name="Media Player"))
#m.name = "Asset Tester" #Maurice Game"
#m.name = "Maurice Game"
#m.name = "Test Grid" #Launcher Lens" #Tester" #Maurice Game"

# box dissapears at 18 - just highlighted
#m.parameters.extend([make_param("gridSize", "18")]) #assetIds", "S3333423432432")]) #1,2,3,4,5")])
#m.parameters.extend([make_param("host", "127.0.0.1%08x%08x%08x%08x"), make_param("port", "12345")]) #12345")])
#m.parameters.extend([make_param("host", "10.0.0.251"), make_param("port", "%x")]) #12345")])
#m.parameters.extend([make_param("host", "10.0.0.251"), make_param("port", "12345")]) #%d")]) #12345")])

#sendmsg(m) #, "startExperience")

#m = msgs.StopExperience()
#m.name = "Monocular"
#sendmsg(m, "stopExperience")
#
#
#def sendFuckedMessage(msg):
#    data = msg.SerializeToString()
#    reallen = len(data)
#    lval = _VarintBytes(99999999999999999) #9999999999999)
#    #len(data))
#    data = lval + data
#
#    lval = _VarintBytes(len(data))
#    return (lval + data)
#
#def sendmsgF(m, field):
#    b = msgs.BlackCoral()
#    getattr(b, field).CopyFrom(m)
#    msg = sendFuckedMessage(b)
#    print("SENDING FUCKED")
#    sock.sendto(msg, (UDP_IP, UDP_PORT))
#
#m = msgs.StopExperience()
#m.name = "Monocular"
#for i in range(10000):
#    sendmsg(m, "stopExperience")
#    time.sleep(0.01)


#
#m = msgs.Handshake()
#m.protocolMajorVersion = 4
#m.protocolMinorVersion = 40
#
#sendmsg(m, "handshake")

#
##### full table of messages phone -> glasses
if False:
    sendmsg(make(msgs.Handshake,
        protocolMajorVersion = 4,
        protocolMinorVersion = 40
    ))



#optional Handshake handshake = 1;
#optional SocketOpenResponse socketOpenResponse = 2;
if False:
    sendmsg(make(msgs.SocketOpenResponse,
            status = 0,
            streamId=0,
        ))


#optional SocketCloseResponse socketCloseResponse = 3;
#optional SocketDataChunk socketDataChunk = 4;
#optional Notification notification = 6;
#    message Notification {
#        repeated NotificationAction actions = 8;
#            message NotificationAction {
#                required string actionIconFileId = 2;
#                repeated RemoteInput inputs = 4;
#                    message RemoteInput {
#                        required bool allowsFreeForm = 2;
#                        required string key = 1;
#                        required string label = 3;
#                        repeated string smartChoices = 4;
#
#                    }
#                required string key = 1;
#                required string title = 3;
#            }
#        optional string appIconFileId = 7;
#        optional string appIdentifier = 5;
#        optional string appName = 6;
#        required string identifier = 1;
#        optional bool isSilent = 10;
#        optional bool isUpdate = 9;
#        optional string previewText = 11;
#        required string text = 3;
#        required string time = 4;
#        required string title = 2;
#    }
if False:

    # notification id is escaped for format strings
    # action key, action title, are escaped correctly
    # RemoteInput in action - smartChoices are escaped and format strings don't work
    #   remote input key is escaped

    # Whatever Identifier you provide for appIconFileId - if they don't previously have it,
    # the glasses will initiate a file transfer with a StartFileTransfer message

    # It looks like appIconFileId is not escaped:
    #       1%d resulted in a request to transfer file id: 1%25d
    ###  It looks like it will auto replace any % with %25 to try to limit the size - which to me
    # says that the string its filling in is probably max 25 length.  But,
    # it doesn't appear to blindly fill in string

    # Confirmed - any instance of '%' is replaced by '%25'

    # additionally, sending a bad icon id, it appears I crashed whatever is managing icons,
    # because all of the sudden no icons display

    # strings that crashed the icon service:
    #       appIconFileId="1%0d", -> got resolved as "1%0D"
    #       appIconFileId="1 %1d", -> got resolved as "1 %1D"
    #       appIconFileId="1 %1s", -> got resolved as "1 %251s"
    #       appIconFileId="1 %1A", -> got resolved as "1 %1A"
    #       appIconFileId="1 %1b", -> Crashed the icon service, but I suspect this is because there are too many active requests to get icons,
    #           on restart, got resolved as "1 %1B"
    #       appIconFileId="1 %1c", -> "1 %1C"
    #       appIconFileId="1 %1e", -> "1 %1E"
    #       appIconFileId="1 %1f", -> "1 %1F"
    #       appIconFileId="1 %1g", -> "1 %251g"
    #       appIconFileId="1 %1h", -> "1 %251g"
    #       appIconFileId="1 %1z", -> "1 %251z"


    #### Things to look into:
    ## When I provide asset id, it tries to start a file transfer - where does that get saved??



    sendmsg(make(msgs.Notification,
                identifier="m1%d", #08x",
                title="title",
                text="text",
                #time="2019-08-02T07:55:00",
                #time="2019-08-02", #T07:55:00",
                time="2019-11-17T10:56:47.648-06:00",
                appIdentifier="co.m",
                appName="app",
                #appIconFileId="1", #None,
                appIconFileId=avail_path, #"../../../../../../../system/etc/1.wav", # %1z", #d", #+'%s'*50, #%%", #08x", #None,
                isUpdate=False,
                isSilent=False,
                previewText="preview",
                #actions=[
                #    make(msgs.NotificationAction,

                #        actionIconFileId="2", #icon:/system/icon/checkmark", #call-answer", #1234",
                #        #inputs=[
                #        #    make(msgs.RemoteInput, allowsFreeForm=False, key="test%08x", label="label2", smartChoices=[
                #        #            "test: %08x",
                #        #            "abc: %d"
                #        #        ]),
                #        #    make(msgs.RemoteInput, allowsFreeForm=False, key="key2", label="label2", smartChoices=[
                #        #            "sc3",
                #        #            "sc4"
                #        #        ])
                #        #],
                #        key="act1%08x",
                #        title="doit%08x"
                #    )
                #],



                #appName="aegray",
                #appIdentifier="com.example.aegray",
                #previewText="pvt",
                #text="hello",
                #time="2019-08-02 07:55:00",
                #title="testing"
            ))


if False:
    sendmsg(make(msgs.RemotePing,
            payload="test"
        ))
#
#optional RemotePing remotePing = 7;
#    message RemotePing {
#        optional string payload = 1;
#    }
#



#optional CurrentTime currentTime = 8;
#    message CurrentTime {
#        required string time = 1;
#        required string timeZone = 2;
#    }
#
if False:
    ### it seems like it validdates decently well, but if you send too long a string,
    # appears to crash, then no longer respond to updates
    #  This makes me think there's a display layer and an updater layer in the background,
    # and the updater layer in the background crashes, requireing a reboot
    #sendmsg(make(msgs.CurrentTime, time="2019-08-02 %02d:%02d", timeZone="CST")) #-%s-%s", timeZone="CST")) #2019-08-04 \0\0:\0\0", timeZone="CST")) #00000000000000000900000000000000000000000000000000000000:00000000000000009:000000000000000000000000"+"\1"*1000, timeZone="CST"))
    sendmsg(make(msgs.CurrentTime, time="2019-08-02 07:25", timeZone="CST"))
    #sendmsg(make(msgs.CurrentTime, time="\x001"*950, timeZone="CST")) #"2019-08-02 07:55", timeZone="CST"))
    #sendmsg(make(msgs.CurrentTime, time="%04d-08-02 07:55", timeZone="CST"))
    #sendmsg(make(msgs.CurrentTime, time="2019-08-01 10:35", timeZone="UTC")) #" + "abcd"*1000, timeZone="CST"))



#optional CalibrateEyeTracking calibrateEyeTracking = 9;
#optional StartInputDevicePairing startInputDevicePairing = 10;
#optional CancelInputDevicePairing cancelInputDevicePairing = 11;
#optional UnpairInputDevice unpairInputDevice = 12;
#optional AppNotificationFilter appNotificationFilter = 13;
#optional DismissNotification dismissNotification = 16;
#    message DismissNotification {
#        required string identifier = 1;
#    }
#optional GetHostByNameResponse getHostByNameResponse = 18;
#    message GetHostByNameResponse {
#        optional int32 errorCode = 4;
#        optional string host = 3;
#        required string name = 1;
#        required Status status = 2;
#    }
#optional SocketError socketError = 19;

if False:
#optional BlackCoralSync sync = 20;
#    message BlackCoralSync {
#        optional FeatureSupportedByCompanion featureSupportedByCompanion = 3;
#            message FeatureSupportedByCompanion {
#                optional bool locationSharing = 1;
#            }
#        optional Settings settings = 1;
#            message Settings {
#                optional AppNotificationBlacklist appNotificationBlacklist = 5;
#                    message AddToAppNotificationBlacklist {
#                        required string appIdentifier = 1;
#                        required string appName = 2;
#                    }
#                optional bool autoDetectDriving = 9;
#                optional string cloudHost = 1;
#                optional NotificationDisplay notificationDisplay = 4;
#                    message NotificationDisplay {
#                        required DisplayLevel level = 1;
#                            enum DisplayLevel {
#                                REDUCED = 0;
#                                FULL = 1;
#                                AUDIO = 2;
#                            }
#                    }
#                optional PlayChime playChime = 7;
#                    message PlayChime {
#
#                    }
#                optional bool preferFahrenheit = 8;
#                optional SetUiCenterOffset setUiCenterOffset = 3;
#                    message SetUiCenterOffset {
#                        required int32 xOffset = 1;
#                        required int32 yOffset = 2;
#                    }
#                optional bool soundOnRingClick = 2;
#                optional float volume = 6;
#
#            }
#        optional State state = 2;
#            message State {
#                optional Account account = 3;
#                    message Account {
#                        optional string accountId = 1;
#
#                    }
#                optional string companionId = 4;
#                optional bool isCalendarEnabled = 5;
#                optional bool isNetReachable = 2;
#                optional SetAuthToken setAuthToken = 1;
#                    message SetAuthToken {
#                        optional string authToken = 1;
#
#                    }
#            }
#
#    }
    sendmsg(make(msgs.BlackCoralSync,
            state=make(msgs.State,
                isNetReachable=True,
            )))
#optional Settings settings = 25;
#optional State state = 26;
#optional StartExperience startExperience = 27;
##m = msgs.StartExperience()
##m.name = "Monocular"
## box dissapears at 18 - just highlighted
##m.parameters.extend([make_param("gridSize", "18")]) #assetIds", "S3333423432432")]) #1,2,3,4,5")])
##m.parameters.extend([make_param("host", "127.0.0.1%08x%08x%08x%08x"), make_param("port", "12345")]) #12345")])
##m.parameters.extend([make_param("host", "10.0.0.251"), make_param("port", "%x")]) #12345")])
##m.parameters.extend([make_param("host", "10.0.0.251"), make_param("port", "12345")]) #%d")]) #12345")])
#
#optional StopExperience stopExperience = 28;
#optional BlackCoralFileTransfer fileTransfer = 29;
#        message BlackCoralFileTransfer {
#            optional FileChunkResponse fileChunkResponse = 2;
#                message FileChunkResponse {
#                    required string id = 1;
#                    required uint32 startByte = 3;
#                    required filetransfer_Status status = 2;
#                }
#            optional StartFileTransferResponse startFileTransferResponse = 1;
#                message StartFileTransferResponse {
#                    optional uint32 checksum = 4;
#                    required string id = 1;
#                    optional uint32 length = 3;
#                    required filetransfer_Status status = 2;
#                }
#        }
#optional BlackCoralUpdate update = 30;
#optional FactoryReset factoryReset = 31;
#optional CaptureLogs captureLogs = 32;
if False:
    sendmsg(make(msgs.CaptureLogs,
        #reportId="bluetooth"
            #state=make(msgs.State,
            #    isNetReachable=True,
            ))

#optional Calendar calendar = 33;
#optional BlackCoralLocation location = 34;
#optional BlackCoralExitPupilAlignment exitPupilAlignment = 35;
#optional RefreshAuthTokenFailed refreshAuthTokenFailed = 36;
#optional SendSmsResponse sendSmsResponse = 37;
#optional BlackCoralSms sms = 38;
#        message BlackCoralSms {
#            optional ContactInfoResponse contactInfoResponse = 6;
#                message ContactInfoResponse {
#                    repeated ContactInfo contactInfo = 1;
#                        message ContactInfo {
#                            required string name = 1;
#                            required string phoneNumber = 2;
#
#                        }
#                }
#            optional Sms smsReceived = 2;
#                message Sms {
#                    optional bool hasNonTextAttachments = 6;
#                    required string id = 1;
#                    optional bool read = 7;
#                    required string senderName = 2;
#                    required string senderNumber = 3;
#                    required string text = 5;
#                    required string timestamp = 4;
#
#                }
#
#
#            optional Sms smsSync = 1;
#            optional Sms smsUpdated = 3;
#            optional SmsSyncCompleted syncCompleted = 5;
#                message SmsSyncCompleted {
#
#                }
#            optional SmsSyncStarted syncStarted = 4;
#                message SmsSyncStarted {
#
#                }
#
#
#        }
#optional BlackCoralFeatures features = 39;
if False:
   # sendmsg(make(msgs.StartExperience,
   #         name="a"*4096
   #         #fileformat="jpg" *200 #1024
   #     ))
   #
    sendmsg(make(msgs.StartExperience,
            name="Enable No-Privacy Logging",
            parameters=[
                make(msgs.ParameterEntry,
                    #key="isStartCommand",
                    key="%s"*400,
                    value="%s"*400,
                    #value="a"*900 #"%s"
                )
            ]
            #parameterNames: "isStartCommand"
            #fileformat="jpg" *200 #1024
        ))
#
#experiences {
#  name: "Enable No-Privacy Logging"
#  parameterNames: "isStartCommand"
#  parameters {
#    name: "isStartCommand"
#    defaultValue: "true"
#  }
#}
#
#
if False:
#    sendmsg(make(msgs.BlackCoralFeatures,
#        featureList = make(msgs.GetFeatureList)
#    ))
#
    sendmsg(make(msgs.StopExperience,
            name="Media Player",
        ))
    sendmsg(make(msgs.StartExperience,
            name="Media Player",
            parameters=[
                make(msgs.ParameterEntry,
                    #key="isStartCommand",
                    key="filePath",
                    #value="/data/data/data/%s/%s/%s",
                    #value="//",
                    #/data/data/data/%s/%s/%s" + "%d"*200,
                    value="/data/data/data/%s/%s/%s" + "%d"*200,
                    #value="a"*900 #"%s"
                )
            ]
            #parameterNames: "isStartCommand"
            #fileformat="jpg" *200 #1024
        ))
#
#        message BlackCoralFeatures {
#            optional GetFeatureList featureList = 1;
#            optional SetEnabledFeatures setEnabledFeatures = 2;
#
#
#        }
#
#

#optional BlackCoralExternalAuthorization externalAuthorization = 40;
#optional BlackCoralLocationSharingControl locationSharingControl = 41;
#optional BlackCoralNavigation navigation = 42;
#optional BlackCoralActivity activity = 43;

if False:
#optional CaptureScreenshot captureScreenshot = 44;

    #### sending too much data here definitely crashes the screenshotting service

    sendmsg(make(msgs.CaptureScreenshot,
            fileformat="jpg"
            #fileformat="jpg" *200 #1024
        ))
       #     #silent=False
       #     state=make(msgs.State,
       #         isNetReachable=True,
       #     )))
#optional BlackCoralFavouriteContacts favouriteContacts = 45;
#optional BlackCoralNoteTaker noteTaker = 46;
#optional BlackCoralTemplatedSettings templatedSettings = 47;
if False:
    # Not sure here
    sendmsg(make(msgs.BlackCoralTemplatedSettings,
        getSettings = make(msgs.GetSettings,
          #  json = "" #....
        )))

    pass


#optional BlackCoralWonderland wonderland = 48;
if False:
    sendmsg(make(msgs.BlackCoralShowcase,
            #getStories = make(msgs.GetStories)
            #startShowcase = make(msgs.StartShowcase)
            #stopShowcase = make(msgs.StopShowcase)
            #stopShowcase = make(msgs.StopShowcase)
            #startStory = make(msgs.StartStory,
            #    contentUri="http://google.com" #static://data"
            #)

            #startShowcase
            # stopShowcase
            # getStories
            # startStory
            # stopStory
        ))
#optional BlackCoralShowcase showcase = 49;
#
#
#

if True:
    sendmsg(make(msgs.BlackCoralFeatures,
            setEnabledFeatures=make(msgs.SetEnabledFeatures,
                id = [

                    "android_action",
                    "battery_lens",
                    "calendar",
                    "daily_briefing",
                    "demo_notes",
                    "demo_tasks",
                    #"disconnect_overlay",
                    "flash_cards",
                    "flynns",
                    "flywheel",
                    #"flywheel2",
                    "go",
                    "headway",
                    "health",
                    "health_digital",
                    "ketchup",
                    #"long_disp_time",
                    "monocular",
                    "noisedog",
                    "notes",
                    "oahu_demo",
                    "pied_piper",
                    "showcase",
                    "sky_captain",
                    #"smart_reply_marian",
                    "sportscaster",
                    "tasks_app",
                    "tasks_filter",
                    "teleprompter",
                    "templated_settings",

                    "testFeature_000",
                    "testFeature_001",
                    "testFeature_100",
                    "testFeature_101",
                    "testFeature_defs",


                    "tour_guide",
                    "trebek",
                    "warm_camera",
                    "weather",
                    "whiterabbit",
                    "wysiwis",

                ]
            )))



#
#
#
#
#
#Got Message:  <class 'BC_pb2.CompanionFeatures'> featureListResponse {
#  featureDefinition {
#    id: "android_action"
#    name: "Android Notification Actions"
#    enabled: true
#    description: "Focals will support Android smartphone notification actions."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "battery_lens"
#    name: "Battery view"
#    enabled: true
#    description: "See the battery level for Focals and Loop"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "calendar"
#    name: "Calendar view"
#    enabled: true
#    description: "See all your calendar events for the day"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "daily_briefing"
#    name: "Morning Briefing"
#    enabled: true
#    description: "Get a quick briefing on what your morning looks like, including the forecast, commute times, and your first calendar event."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "disconnect_overlay"
#    name: "Disconnectivity Overlay"
#    enabled: false
#    description: "Inform the user of disconnectivity with a transparent overlay."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "flash_cards"
#    name: "Language Flash Cards"
#    enabled: false
#    description: "Learn languages using with flash cards on Focals. We support French, Japanese, Chinese (Mandarin), Arabic, and Portuguese (Brazil)"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "flynns"
#    name: "Game Arcade"
#    enabled: false
#    description: "Play games on Focals"
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "flywheel"
#    name: "Longpress Action Menu"
#    enabled: true
#    description: "Press and hold Loop to bring up a quick action menu."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "flywheel2"
#    name: "Quick Launch"
#    enabled: false
#    description: "Press and hold the Loop to bring up a quick action menu."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "go"
#    name: "Places view"
#    enabled: true
#    description: "See your current location, a list of all your saved places, and start a trip from Focals."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "headway"
#    name: "Commute Status"
#    enabled: true
#    description: "See the ETA of your commute to home and work"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "health"
#    name: "Fitness Tracking"
#    enabled: true
#    description: "Track your physical health from Google Fit."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "health_digital"
#    name: "Screen Time"
#    enabled: true
#    description: "Track how much phone screen time you have saved by wearing Focals"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "ketchup"
#    name: "Conversation Awareness"
#    enabled: true
#    description: "Focals will hold back incoming notifications while you are in a conversation and displays a summary of what you missed once you are done."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "long_disp_time"
#    name: "Extend Display On Time"
#    enabled: false
#    description: "When not interacting with your glasses, the display will stay on a little longer before fading out."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "monocular"
#    name: "Enable Monocular support"
#    enabled: false
#    description: "Enable support for Monocular app on Focals."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "noisedog"
#    name: "What\'s Playing?"
#    enabled: true
#    description: "Discover what music is playing around you and add it to your liked songs on Spotify."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "notes"
#    name: "Notes"
#    enabled: true
#    description: "View and favorite notes with Focals and any supported"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "oahu_demo"
#    name: "Demo mode for Oahu"
#    enabled: false
#    description: "Overall demo mode enable/disable control."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "pied_piper"
#    name: "Spotify"
#    enabled: true
#    description: "See what\'s playing on Spotify. If you have Spotify Premium, control music with Loop."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "showcase"
#    name: "Showcase"
#    enabled: true
#    description: "Explore a quick walkthrough of the latest features on Focals"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "sky_captain"
#    name: "Flights"
#    enabled: false
#    description: "Track the status of upcoming flights synced from your calendar, including any delays or changes. Send a message to let others know where you are during your trip."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "smart_reply_marian"
#    name: "New Text Smart Replies"
#    enabled: false
#    description: "A new an improved text smart replies engine"
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "sportscaster"
#    name: "Sports Updates"
#    enabled: true
#    description: "Keep up with your favorite NBA, NHL, NFL or MLB teams. Get updated scores and play-by-play details from your favorite teams."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "tasks_app"
#    name: "Tasks"
#    enabled: true
#    description: "Add tasks and mark them as complete using Focals and any supported Task app."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "teleprompter"
#    name: "Focals Connect"
#    enabled: true
#    description: "Connect Focals with your Google Slides presentations. View speaker notes and control slides from Focals"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "templated_settings"
#    name: "Additional Settings"
#    enabled: true
#    description: "Settings page in the Focals app including additional settings fetched dynamically from Focals."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "testFeature_000"
#    name: "Disabled, Invisible, Uneditable"
#    enabled: false
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "testFeature_001"
#    name: "Disabled, Invisible, Editable"
#    enabled: false
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "testFeature_100"
#    name: "Enabled, Invisible, Uneditable"
#    enabled: true
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "testFeature_101"
#    name: "Enabled, Invisible, Editable"
#    enabled: true
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "testFeature_defs"
#    name: "Default enabled, visible, editable"
#    enabled: false
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "tour_guide"
#    name: "Venue Tips"
#    enabled: false
#    description: "Discover popular tips about nearby places"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "trebek"
#    name: "Trivia Game"
#    enabled: false
#    description: "Play trivia against other Focals users. New games arrive daily."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "warm_camera"
#    name: "Warm Camera Mode"
#    enabled: false
#    description: "Ensure that the camera is warm."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "weather"
#    name: "Weather view"
#    enabled: true
#    description: "See the current and extended weather forecast"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "whiterabbit"
#    name: "Meeting responses"
#    enabled: true
#    description: "Let others know that you are running late to a meeting or that you won\'t make it"
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "wysiwis"
#    name: "Lenscast"
#    enabled: true
#    description: "Share what you are seeing on Focals with others by mirroring your display on your phone"
#    visible: false
#    editable: false
#  }
#}
#
#
#Got Message:  <class 'BC_pb2.CompanionFeatures'> featureListResponse {
#  featureDefinition {
#    id: "android_action"
#    name: "Android Notification Actions"
#    enabled: true
#    description: "Focals will support Android smartphone notification actions."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "battery_lens"
#    name: "Battery view"
#    enabled: true
#    description: "See the battery level for Focals and Loop"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "calendar"
#    name: "Calendar view"
#    enabled: true
#    description: "See all your calendar events for the day"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "daily_briefing"
#    name: "Morning Briefing"
#    enabled: true
#    description: "Get a quick briefing on what your morning looks like, including the forecast, commute times, and your first calendar event."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "disconnect_overlay"
#    name: "Disconnectivity Overlay"
#    enabled: false
#    description: "Inform the user of disconnectivity with a transparent overlay."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "flash_cards"
#    name: "Language Flash Cards"
#    enabled: false
#    description: "Learn languages using with flash cards on Focals. We support French, Japanese, Chinese (Mandarin), Arabic, and Portuguese (Brazil)"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "flynns"
#    name: "Game Arcade"
#    enabled: false
#    description: "Play games on Focals"
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "flywheel"
#    name: "Longpress Action Menu"
#    enabled: true
#    description: "Press and hold Loop to bring up a quick action menu."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "flywheel2"
#    name: "Quick Launch"
#    enabled: false
#    description: "Press and hold the Loop to bring up a quick action menu."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "go"
#    name: "Places view"
#    enabled: true
#    description: "See your current location, a list of all your saved places, and start a trip from Focals."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "headway"
#    name: "Commute Status"
#    enabled: true
#    description: "See the ETA of your commute to home and work"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "health"
#    name: "Fitness Tracking"
#    enabled: true
#    description: "Track your physical health from Google Fit."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "health_digital"
#    name: "Screen Time"
#    enabled: true
#    description: "Track how much phone screen time you have saved by wearing Focals"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "ketchup"
#    name: "Conversation Awareness"
#    enabled: true
#    description: "Focals will hold back incoming notifications while you are in a conversation and displays a summary of what you missed once you are done."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "long_disp_time"
#    name: "Extend Display On Time"
#    enabled: false
#    description: "When not interacting with your glasses, the display will stay on a little longer before fading out."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "monocular"
#    name: "Enable Monocular support"
#    enabled: false
#    description: "Enable support for Monocular app on Focals."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "noisedog"
#    name: "What\'s Playing?"
#    enabled: true
#    description: "Discover what music is playing around you and add it to your liked songs on Spotify."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "notes"
#    name: "Notes"
#    enabled: true
#    description: "View and favorite notes with Focals and any supported"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "oahu_demo"
#    name: "Demo mode for Oahu"
#    enabled: false
#    description: "Overall demo mode enable/disable control."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "pied_piper"
#    name: "Spotify"
#    enabled: true
#    description: "See what\'s playing on Spotify. If you have Spotify Premium, control music with Loop."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "showcase"
#    name: "Showcase"
#    enabled: true
#    description: "Explore a quick walkthrough of the latest features on Focals"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "sky_captain"
#    name: "Flights"
#    enabled: false
#    description: "Track the status of upcoming flights synced from your calendar, including any delays or changes. Send a message to let others know where you are during your trip."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "smart_reply_marian"
#    name: "New Text Smart Replies"
#    enabled: false
#    description: "A new an improved text smart replies engine"
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "sportscaster"
#    name: "Sports Updates"
#    enabled: true
#    description: "Keep up with your favorite NBA, NHL, NFL or MLB teams. Get updated scores and play-by-play details from your favorite teams."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "tasks_app"
#    name: "Tasks"
#    enabled: true
#    description: "Add tasks and mark them as complete using Focals and any supported Task app."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "teleprompter"
#    name: "Focals Connect"
#    enabled: true
#    description: "Connect Focals with your Google Slides presentations. View speaker notes and control slides from Focals"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "templated_settings"
#    name: "Additional Settings"
#    enabled: true
#    description: "Settings page in the Focals app including additional settings fetched dynamically from Focals."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "testFeature_000"
#    name: "Disabled, Invisible, Uneditable"
#    enabled: false
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "testFeature_001"
#    name: "Disabled, Invisible, Editable"
#    enabled: false
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "testFeature_100"
#    name: "Enabled, Invisible, Uneditable"
#    enabled: true
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "testFeature_101"
#    name: "Enabled, Invisible, Editable"
#    enabled: true
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "testFeature_defs"
#    name: "Default enabled, visible, editable"
#    enabled: false
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "tour_guide"
#    name: "Venue Tips"
#    enabled: false
#    description: "Discover popular tips about nearby places"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "trebek"
#    name: "Trivia Game"
#    enabled: false
#    description: "Play trivia against other Focals users. New games arrive daily."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "warm_camera"
#    name: "Warm Camera Mode"
#    enabled: false
#    description: "Ensure that the camera is warm."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "weather"
#    name: "Weather view"
#    enabled: true
#    description: "See the current and extended weather forecast"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "whiterabbit"
#    name: "Meeting responses"
#    enabled: true
#    description: "Let others know that you are running late to a meeting or that you won\'t make it"
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "wysiwis"
#    name: "Lenscast"
#    enabled: true
#    description: "Share what you are seeing on Focals with others by mirroring your display on your phone"
#    visible: false
#    editable: false
#  }
#}
#
#
#Got Message:  <class 'BC_pb2.CompanionFeatures'> featureListResponse {
#  featureDefinition {
#    id: "android_action"
#    name: "Android Notification Actions"
#    enabled: true
#    description: "Focals will support Android smartphone notification actions."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "battery_lens"
#    name: "Battery view"
#    enabled: true
#    description: "See the battery level for Focals and Loop"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "calendar"
#    name: "Calendar view"
#    enabled: true
#    description: "See all your calendar events for the day"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "daily_briefing"
#    name: "Morning Briefing"
#    enabled: true
#    description: "Get a quick briefing on what your morning looks like, including the forecast, commute times, and your first calendar event."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "disconnect_overlay"
#    name: "Disconnectivity Overlay"
#    enabled: false
#    description: "Inform the user of disconnectivity with a transparent overlay."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "flash_cards"
#    name: "Language Flash Cards"
#    enabled: false
#    description: "Learn languages using with flash cards on Focals. We support French, Japanese, Chinese (Mandarin), Arabic, and Portuguese (Brazil)"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "flynns"
#    name: "Game Arcade"
#    enabled: false
#    description: "Play games on Focals"
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "flywheel"
#    name: "Longpress Action Menu"
#    enabled: true
#    description: "Press and hold Loop to bring up a quick action menu."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "flywheel2"
#    name: "Quick Launch"
#    enabled: false
#    description: "Press and hold the Loop to bring up a quick action menu."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "go"
#    name: "Places view"
#    enabled: true
#    description: "See your current location, a list of all your saved places, and start a trip from Focals."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "headway"
#    name: "Commute Status"
#    enabled: true
#    description: "See the ETA of your commute to home and work"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "health"
#    name: "Fitness Tracking"
#    enabled: true
#    description: "Track your physical health from Google Fit."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "health_digital"
#    name: "Screen Time"
#    enabled: true
#    description: "Track how much phone screen time you have saved by wearing Focals"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "ketchup"
#    name: "Conversation Awareness"
#    enabled: true
#    description: "Focals will hold back incoming notifications while you are in a conversation and displays a summary of what you missed once you are done."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "long_disp_time"
#    name: "Extend Display On Time"
#    enabled: false
#    description: "When not interacting with your glasses, the display will stay on a little longer before fading out."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "monocular"
#    name: "Enable Monocular support"
#    enabled: false
#    description: "Enable support for Monocular app on Focals."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "noisedog"
#    name: "What\'s Playing?"
#    enabled: true
#    description: "Discover what music is playing around you and add it to your liked songs on Spotify."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "notes"
#    name: "Notes"
#    enabled: true
#    description: "View and favorite notes with Focals and any supported"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "oahu_demo"
#    name: "Demo mode for Oahu"
#    enabled: false
#    description: "Overall demo mode enable/disable control."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "pied_piper"
#    name: "Spotify"
#    enabled: true
#    description: "See what\'s playing on Spotify. If you have Spotify Premium, control music with Loop."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "showcase"
#    name: "Showcase"
#    enabled: true
#    description: "Explore a quick walkthrough of the latest features on Focals"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "sky_captain"
#    name: "Flights"
#    enabled: false
#    description: "Track the status of upcoming flights synced from your calendar, including any delays or changes. Send a message to let others know where you are during your trip."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "smart_reply_marian"
#    name: "New Text Smart Replies"
#    enabled: false
#    description: "A new an improved text smart replies engine"
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "sportscaster"
#    name: "Sports Updates"
#    enabled: true
#    description: "Keep up with your favorite NBA, NHL, NFL or MLB teams. Get updated scores and play-by-play details from your favorite teams."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "tasks_app"
#    name: "Tasks"
#    enabled: true
#    description: "Add tasks and mark them as complete using Focals and any supported Task app."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "teleprompter"
#    name: "Focals Connect"
#    enabled: true
#    description: "Connect Focals with your Google Slides presentations. View speaker notes and control slides from Focals"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "templated_settings"
#    name: "Additional Settings"
#    enabled: true
#    description: "Settings page in the Focals app including additional settings fetched dynamically from Focals."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "testFeature_000"
#    name: "Disabled, Invisible, Uneditable"
#    enabled: false
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "testFeature_001"
#    name: "Disabled, Invisible, Editable"
#    enabled: false
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "testFeature_100"
#    name: "Enabled, Invisible, Uneditable"
#    enabled: true
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "testFeature_101"
#    name: "Enabled, Invisible, Editable"
#    enabled: true
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "testFeature_defs"
#    name: "Default enabled, visible, editable"
#    enabled: false
#    description: "For Feature Testing only. Should never be seen in KCA, nor referenced anywhere in black-coral."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "tour_guide"
#    name: "Venue Tips"
#    enabled: false
#    description: "Discover popular tips about nearby places"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "trebek"
#    name: "Trivia Game"
#    enabled: false
#    description: "Play trivia against other Focals users. New games arrive daily."
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "warm_camera"
#    name: "Warm Camera Mode"
#    enabled: false
#    description: "Ensure that the camera is warm."
#    visible: false
#    editable: true
#  }
#  featureDefinition {
#    id: "weather"
#    name: "Weather view"
#    enabled: true
#    description: "See the current and extended weather forecast"
#    visible: true
#    editable: true
#  }
#  featureDefinition {
#    id: "whiterabbit"
#    name: "Meeting responses"
#    enabled: true
#    description: "Let others know that you are running late to a meeting or that you won\'t make it"
#    visible: false
#    editable: false
#  }
#  featureDefinition {
#    id: "wysiwis"
#    name: "Lenscast"
#    enabled: true
#    description: "Share what you are seeing on Focals with others by mirroring your display on your phone"
#    visible: false
#    editable: false
#  }
#}
#
#
#Got Message:  <class 'BC_pb2.LaunchableExperiences'> experiences {
#  name: "Asset Tester"
#  parameterNames: "assetIds"
#  parameters {
#    name: "assetIds"
#    defaultValue: ""
#  }
#}
#experiences {
#  name: "Balloons"
#}
#experiences {
#  name: "Calibration"
#  parameterNames: "calibrationPoints"
#  parameterNames: "calibrationTime"
#  parameterNames: "gridSize"
#  parameterNames: "userName"
#  parameters {
#    name: "calibrationPoints"
#    defaultValue: "4"
#  }
#  parameters {
#    name: "calibrationTime"
#    defaultValue: "1000"
#  }
#  parameters {
#    name: "gridSize"
#    defaultValue: "5"
#  }
#  parameters {
#    name: "userName"
#    defaultValue: ""
#  }
#}
#experiences {
#  name: "Test Grid"
#  parameterNames: "gridSize"
#  parameterNames: "userName"
#  parameters {
#    name: "gridSize"
#    defaultValue: "5"
#  }
#  parameters {
#    name: "userName"
#    defaultValue: ""
#  }
#}
#experiences {
#  name: "Compose Experience"
#  parameterNames: "message"
#  parameterNames: "successPrompt"
#  parameters {
#    name: "message"
#    defaultValue: "Hello World"
#  }
#  parameters {
#    name: "successPrompt"
#    defaultValue: "Message Sent"
#  }
#}
#experiences {
#  name: "Exit Pupil Alignment with Color Alignment"
#}
#experiences {
#  name: "Launcher Lens"
#}
#experiences {
#  name: "Geolocation Logging"
#}
#experiences {
#  name: "Konacast Service"
#  parameterNames: "castName"
#  parameterNames: "host"
#  parameterNames: "port"
#  parameters {
#    name: "castName"
#    defaultValue: "myCast"
#  }
#  parameters {
#    name: "host"
#    defaultValue: "konacast.thalmiclabs.com"
#  }
#  parameters {
#    name: "port"
#    defaultValue: "80"
#  }
#}
#experiences {
#  name: "Map Test Experience"
#}
#experiences {
#  name: "Monocular"
#  parameterNames: "host"
#  parameterNames: "port"
#  parameters {
#    name: "host"
#    defaultValue: ""
#  }
#  parameters {
#    name: "port"
#    defaultValue: ""
#  }
#}
#experiences {
#  name: "Music Identification"
#}
#experiences {
#  name: "Enable No-Privacy Logging"
#  parameterNames: "isStartCommand"
#  parameters {
#    name: "isStartCommand"
#    defaultValue: "true"
#  }
#}
#experiences {
#  name: "Maurice Game"
#}
#experiences {
#  name: "Retail Demo Settings"
#  parameterNames: "uberSandbox"
#  parameters {
#    name: "uberSandbox"
#    defaultValue: "0"
#  }
#}
#experiences {
#  name: "Snoozed Notification Experience"
#  parameterNames: "snoozedNotificationCount"
#  parameters {
#    name: "snoozedNotificationCount"
#    defaultValue: "10"
#  }
#}
#experiences {
#  name: "Toggle Exit Pupil"
#  parameterNames: "epToEnable"
#  parameters {
#    name: "epToEnable"
#    defaultValue: ""
#  }
#}
#experiences {
#  name: "Toggle Exit Pupil (pty)"
#  parameterNames: "epToEnable"
#  parameters {
#    name: "epToEnable"
#    defaultValue: ""
#  }
#}
#experiences {
#  name: "Media Player"
#  parameterNames: "filePath"
#  parameters {
#    name: "filePath"
#    defaultValue: "/data/kmp/"
#  }
#}
#experiences {
#  name: "EP Illuminator"
#  parameterNames: "filePath"
#  parameters {
#    name: "filePath"
#    defaultValue: "/data/illum/default.png"
#  }
#}
#experiences {
#  name: "Self-Guided EP Positioning"
#  parameterNames: "filePath"
#  parameters {
#    name: "filePath"
#    defaultValue: "/data/pos/default.4ep.png"
#  }
#}
#experiences {
#  name: "Toggle Display Timeout"
#}
#experiences {
#  name: "Uber Product Override"
#  parameterNames: "productOverride"
#  parameters {
#    name: "productOverride"
#    defaultValue: "UberX"
#  }
#}
#
#
#
