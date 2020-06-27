package com.example.bluetooth_test2;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.ParcelUuid;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

//import com.squareup.wire.Message;
import com.squareup.wire.ProtoWriter;
import com.squareup.wire.ProtoReader;
import com.squareup.wire.internal.Internal;

import org.greenrobot.eventbus.EventBus;
import org.greenrobot.eventbus.Subscribe;
import org.greenrobot.eventbus.ThreadMode;

import java.io.BufferedWriter;
import java.io.EOFException;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.nio.charset.Charset;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.TimeZone;
import java.util.UUID;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

import co.glassio.blackcoral.BlackCoral;
import co.glassio.blackcoral.CaptureLogs;
import co.glassio.blackcoral.DismissNotification;
import co.glassio.blackcoral.GetHostByNameResponse;
import co.glassio.blackcoral.LCompanion;
import co.glassio.blackcoral.Handshake;
import co.glassio.blackcoral.Notification;
import co.glassio.blackcoral.NotificationAction;
import co.glassio.blackcoral.ParameterEntry;
import co.glassio.blackcoral.SocketCloseResponse;
import co.glassio.blackcoral.SocketDataChunk;
import co.glassio.blackcoral.SocketError;
import co.glassio.blackcoral.SocketOpen;
import co.glassio.blackcoral.SocketOpenResponse;
import co.glassio.blackcoral.StartExperience;
import co.glassio.blackcoral.StartInputDevicePairing;
import co.glassio.blackcoral.Status;
import co.glassio.blackcoral.StopExperience;
import co.glassio.util.VarInt;
import okio.Buffer;
import okio.BufferedSource;
import okio.ByteString;
import okio.Okio;
import okio.Sink;
import okio.Source;







public class MainActivity extends AppCompatActivity implements ActivityCompat.OnRequestPermissionsResultCallback {
    private static final String TAG = "AEGRAY";
    private static final int MAX_CHUNK_SIZE = 950;
    private static final int REQUEST_ENABLE_BT = 1;
    //private static final String FOCALS_MAC = "00:00:00:C1:B2:D2";
    private static final String FOCALS_MAC = "00:00:00:1C:1E:B9"; //C1:B2:D2";
    private static final String COMP_MAC = "9C:B6:D0:E8:27:88";


    private static final UUID FOCALS_UUID     = UUID.fromString("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"); // this was replaced for push to github
    private static final UUID FOCALS_DBG_UUID = UUID.fromString("00000000-DECA-FADE-DECA-DEAFDECACAFF");
    private static final SimpleDateFormat ISO8601_FORMAT = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSZZZZZ", Locale.US);

    private static final boolean USE_LOCAL_PRESENT = true;
    private static final String FIXED_DUMMY_IP = "1.1.1.1";
    private static boolean FULL_INTERCEPT = true;


    TextView text_connected_;

    // Bluetooth + connection  stuff
    Executor executor_ = Executors.newSingleThreadExecutor();
    BluetoothAdapter btAdapter_;
    BluetoothDevice btDevice_;
    BluetoothSocket btSocket_;
    Source data_source_;
    Sink data_sink_;
    ConnectTask connectTask_;

    PresentWebsocketManager ws_mgr_ = new PresentWebsocketManager();

    SocketManager sock_mgr_ = new SocketManager(executor_);

    EventBus evbus_ = new EventBus(); // messages from device
    boolean stopRequested_ = false;

    // receiving stuff
    Buffer recv_data_ = new Buffer(); // buffer framed data
    long pending_frame_size_ = 0;

    AnkiCardPresentationProvider anki_cards_;
    StreamingTextPresentationProvider text_cards_ = new StreamingTextPresentationProvider();
    AudioSubtitlePresentationProvider subtitle_cards_;

    boolean connected_ = false;
    boolean handshaked_ = false;





    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data)
    {
        if (requestCode == REQUEST_ENABLE_BT)
        {
            Log.i(TAG, "Bluetooth enabled");
            connect();
        }
    }

    public void onRequestPermissionsResult (int requestCode, String[] permissions, int[] grantResults) {
        if (requestCode==0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            Log.i(TAG, "Got permissions");
            anki_cards_.gotPermissions();
        } else {
            Toast.makeText(MainActivity.this, "Permission denied", Toast.LENGTH_LONG).show();
        }
    }

    public void switchToPresentation(PresentationProvider pnew) {
        PresentationProvider pp = ws_mgr_.getPresentationProvider();
        if (pp != null) {
            if (pp == pnew) {
                return;
            }
            pp.onClose();
        }

        ws_mgr_.setPresentationProvider(pnew);
        if (ws_mgr_.isOpen()) {
            pnew.resetPresentation();
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);


        anki_cards_ = new AnkiCardPresentationProvider(this);
        subtitle_cards_ = new AudioSubtitlePresentationProvider(this);

        evbus_.register(this);

        text_connected_ = findViewById(R.id.textConnecteed);
        text_connected_.setText("Not connected");

        ws_mgr_.setPresentationProvider(anki_cards_);
        //ws_mgr_.setPresentationProvider(text_cards_);
        //ws_mgr_.setPresentationProvider(subtitle_cards_);


        anki_cards_.setPresenter(ws_mgr_);
        text_cards_.setPresenter(ws_mgr_);
        subtitle_cards_.setPresenter(ws_mgr_);

        ws_mgr_.setListener(new PresentWebsocketManager.IListener() {
            public void onMessage(BlackCoral bc, Buffer b) {
                if (FULL_INTERCEPT) {
                    sendMessage(bc, b);
                } else {
                    if (b != null)
                        Log.i(TAG, "WSMGR would send: " + b.readString(Charset.defaultCharset()));
                }
            }
        });
        sock_mgr_.setListener(new SocketManager.ISocketManagerListener() {
            public void onSocketOpenResult(int id, boolean success, int error_code)
            {

                sendMessage(new BlackCoral.Builder().socketOpenResponse(new SocketOpenResponse(
                        id, success ? co.glassio.blackcoral.Status.OK : Status.ERROR,
                        success ? null : Integer.valueOf(error_code))).build(), null);

//                sendMessage(new BlackCoral.Builder().socketDataChunk(new SocketDataChunk(
//                                m.socketDataChunk.streamId)).build(),
//                        new okio.Buffer().writeString(
//                                "HTTP/1.1 101 Switching Protocols\n" +
//                                        "Upgrade: websocket\n" +
//                                        "Connection: Upgrade\n" +
//                                        "Sec-WebSocket-Accept: LjmxOZMtbAOYENrqfwBlETbBRfo=\n" +
//                                        "Date: Sun, 20 Oct 2019 01:07:54 GMT\n" +
//                                        "Server: Python/3.7 websockets/8.0.2\n" +
//                                        "\n", Charset.defaultCharset()));


            }

            public void onSocketError(int id, int error_code) {
                Log.e(TAG, "Got socket error: id=" + id + " error=" + error_code);
                sendMessage(new BlackCoral.Builder().socketError(new SocketError(id, error_code)).build(), null);
            }

            public void onSocketData(int id, Buffer data) {
                Buffer bc = data.clone();
                String s = bc.readString(Charset.defaultCharset());



                Buffer b2 = data.clone();
                String s2 = "";
                try {
                    for (int i = 0; i < b2.size(); ++i) {
                        int x = b2.readByte();
                        s2 = s2 + "," + x;
                    }
                } catch (EOFException e) {
                    Log.e(TAG, "EOF exception");
                }

                Log.d(TAG, "Sending sock data raw to glasses: " + s2.length() + ": " + s2); //StringUtils.getHexValues(data.clone()));

                Log.d(TAG, "Sending sock data raw to glasses: " + data.size() + ": " + StringUtils.getHexValues(data.clone()));

                Log.i(TAG, "Sending sock chunk to glasses: " + s.length() + ": " + s);

                sendMessage(new BlackCoral.Builder().socketDataChunk(new SocketDataChunk(id)).build(),
                                    data);
            }

            public void onSocketCloseResult(int id, boolean success, int error_code) {
                Log.i(TAG, "onSocketCloseResult: id=" + id + " success=" + success + " errcode=" + error_code);
                sendMessage(new BlackCoral.Builder().socketCloseResponse(new SocketCloseResponse(id,
                                    success ? Status.OK : Status.ERROR,
                                    //success ? co.glassio.blackcoral.Status.OK : Status.ERROR
                                    success ? null : Integer.valueOf(error_code)
                                )).build(), null);
            }
        });

        findViewById(R.id.buttonPAnki).setOnClickListener((new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                Log.i(TAG, "P Anki clicked");
                switchToPresentation(anki_cards_);
            }
        }));
        findViewById(R.id.buttonPSubtitle).setOnClickListener((new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                Log.i(TAG, "P Subtitle clicked");
                switchToPresentation(subtitle_cards_);
            }
        }));
        findViewById(R.id.buttonPText).setOnClickListener((new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                Log.i(TAG, "P Text clicked");
                switchToPresentation(text_cards_);
            }
        }));

        findViewById(R.id.buttonFileTransfer).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.i(TAG, "Collect input logs");
                // arg is report Id
                sendMessage(new BlackCoral.Builder().captureLogs(new CaptureLogs(null)).build(), null);
            }
        });


        findViewById(R.id.buttonCollectLogs).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.i(TAG, "Collect input logs");
                // arg is report Id
                sendMessage(new BlackCoral.Builder().captureLogs(new CaptureLogs(null)).build(), null);
            }
        });
        findViewById(R.id.buttonPairInput).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.i(TAG, "Collect input logs");
                // arg is report Id
                sendMessage(new BlackCoral.Builder().startInputDevicePairing(new StartInputDevicePairing()).build(), null);
            }
        });



        findViewById(R.id.buttonDecks).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                Log.i(TAG, "Deck query clicked");
                anki_cards_.lookupDecks();
            }
        });
        findViewById(R.id.button).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                Log.i(TAG, "Button clicked");
                btAdapter_ = BluetoothAdapter.getDefaultAdapter();
                if (btAdapter_ == null) {
                    Log.i(TAG, "Bluetooth not available");
                    return;
                }
                if (!btAdapter_.isEnabled()) {
                    Log.i(TAG, "Requesting to start bluetooth");
                    Intent btIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
                    startActivityForResult(btIntent, REQUEST_ENABLE_BT);
                }
                else
                {
                    connect();
                }
            }
        });
        findViewById(R.id.buttonStartExp).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                if (handshaked_) {
                    Log.i(TAG, "Button start exp clicked");
                    //sendMessage(new BlackCoral.Builder().startExperience(new StartExperience("Balloons", new ArrayList<ParameterEntry>())).build(), null);
                    //sendMessage(new BlackCoral.Builder().startExperience(new StartExperience("Maurice Game", new ArrayList<ParameterEntry>())).build(), null);
                    //ArrayList<ParameterEntry> l = new ArrayList<ParameterEntry>();
                    //l.add(new ParameterEntry("filePath", "/data")); //sdcard/Downloads"));
                    //sendMessage(new BlackCoral.Builder().startExperience(new StartExperience("Media Player", l)).build(), null);


                    ArrayList<ParameterEntry> l = new ArrayList<ParameterEntry>();
                    //l.add(new ParameterEntry("castName", "testcast"));
                    l.add(new ParameterEntry("host", "10.0.0.148"));
                    l.add(new ParameterEntry("port", "8002"));

                    //sendMessage(new BlackCoral.Builder().startExperience(new StartExperience("Konacast Service", l)).build(), null);
                    sendMessage(new BlackCoral.Builder().startExperience(new StartExperience("Monocular", l)).build(), null);
                }
            }
        });
        findViewById(R.id.buttonStopExp).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                if (handshaked_) {
                    Log.i(TAG, "Button stop exp clicked");
                    //sendMessage(new BlackCoral.Builder().stopExperience(new StopExperience("Balloons")).build(), null);
                    //sendMessage(new BlackCoral.Builder().stopExperience(new StopExperience("Maurice Game")).build(), null);
                    //sendMessage(new BlackCoral.Builder().stopExperience(new StopExperience("Media Player")).build(), null);
                    //sendMessage(new BlackCoral.Builder().stopExperience(new StopExperience("Konacast Service")).build(), null);
                    sendMessage(new BlackCoral.Builder().stopExperience(new StopExperience("Monocular")).build(), null);
                }
            }
        });
        findViewById(R.id.buttonNotify).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {


                //try {
                //    BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
                //    Method getUuidsMethod = BluetoothAdapter.class.getDeclaredMethod("getUuids", null);
                //    ParcelUuid[] uuids = (ParcelUuid[]) getUuidsMethod.invoke(adapter, null);

                //    if(uuids != null) {
                //        for (ParcelUuid uuid : uuids) {
                //            Log.d(TAG, "UUID: " + uuid.getUuid().toString());
                //        }
                //    }else{
                //        Log.d(TAG, "Uuids not found, be sure to enable Bluetooth!");
                //    }

                //} catch (NoSuchMethodException e) {
                //    e.printStackTrace();
                //} catch (IllegalAccessException e) {
                //    e.printStackTrace();
                //} catch (InvocationTargetException e) {
                //    e.printStackTrace();
                //}
                if (handshaked_) {
                    Log.i(TAG, "Button notify ");

                    ISO8601_FORMAT.setTimeZone(TimeZone.getDefault());
                    long curt = System.currentTimeMillis();
                    Log.i(TAG, "Date str is: " + (ISO8601_FORMAT.format(new Date(curt)))); // time string

                    sendMessage(new BlackCoral.Builder().notification(new Notification.Builder()
                            .identifier("adam1")  // unique key for notification
                            .title("Title")  // title for notification
                            .text("Text") // text of notification
                            .time(ISO8601_FORMAT.format(new Date(curt))) // time string
                            .appIdentifier("co.adams_app") // package name / app identifier
                            .appName("ADAMSAPP") // app name
                            .appIconFileId(null) // icon file id
                            .actions(new ArrayList<NotificationAction>()) // actions
                            .isUpdate(false) // is update
                            .isSilent(false) // is silent
                            .previewText("PreviewText") // preview text
                            .build()).build(), null);

                            //"FullText",
                            //curt,
                            //new LinkedHashMap())).build(), null);

                }
            }
        });
        findViewById(R.id.buttonDismissNotify).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view)
            {
                if (handshaked_) {
                    Log.i(TAG, "Button dismiss notify ");

                    sendMessage(new BlackCoral.Builder().dismissNotification(new DismissNotification("adam1")).build(), null);
                }
            }
        });


    }




    /////////////////// Connection opening stuff
    private class ConnectTask extends AsyncTask<Void, Void, Boolean> {
        BluetoothSocket socket;

        private ConnectTask(BluetoothSocket s)
        {
            this.socket = s;
        }

        public Boolean doInBackground(Void... voidArr) {
            try{
                Log.i(TAG, "calling connect() direct");
                this.socket.connect();
                return true;
            } catch (IOException e) {
                Log.e(TAG, "GOT IOEXCEPTION B: " + e.toString());
                return false;
            } catch (Throwable e) {
                Log.e(TAG, "GOT THROWABLE: " + e.toString());
                throw e;
            }
        }
    }

    private void connect()
    {
        if (connected_) return;

        Log.i(TAG, "CALLING connect");
        btDevice_ = btAdapter_.getRemoteDevice(FOCALS_MAC);
        int bondState = btDevice_.getBondState();
        Log.i(TAG, "BOND STATE IS :" + bondState);

        BluetoothDevice btDevice_ = btAdapter_.getRemoteDevice(FOCALS_MAC);

        //try {
            //BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
            //Method getUuidsMethod = BluetoothAdapter.class.getDeclaredMethod("getUuids", null);
            ParcelUuid[] uuids = btDevice_.getUuids(); //ParcelUuid[]) getUuidsMethod.invoke(adapter, null);

            if(uuids != null) {
                for (ParcelUuid uuid : uuids) {
                    Log.d(TAG, "UUID: " + uuid.getUuid().toString());
                }
            }else{
                Log.d(TAG, "Uuids not found, be sure to enable Bluetooth!");
            }

        //} catch (NoSuchMethodException e) {
        //    e.printStackTrace();
        //} catch (IllegalAccessException e) {
        //    e.printStackTrace();
        //} catch (InvocationTargetException e) {
        //    e.printStackTrace();
       // }

        text_connected_.setText("Connecting...");
        try {
            btSocket_ = btDevice_.createRfcommSocketToServiceRecord(FOCALS_UUID);
            connectTask_ = new ConnectTask(btSocket_) {
                public void onPostExecute(Boolean b) {
                    if (b.booleanValue()) {
                        MainActivity.this.onBluetoothConnected(this.socket);
                        Log.i(TAG, "Connected");
                    } else {
                        Log.e(TAG, "COULD NOT CONNECT");
                        MainActivity.this.onBluetoothDisconnected();
                    }
                }
            };
            this.connectTask_.executeOnExecutor(this.executor_, new Void[0]);
        } catch (IOException e) {
            Log.e(TAG, "Got IOEXCEPT A: " + e.toString());
            MainActivity.this.onBluetoothDisconnected();
            //this.text_connected_.setText("Not connected");
        }
    }

    @Subscribe(threadMode = ThreadMode.MAIN)
    public void onDisconnect(DisconnectedEvent d) {
        onBluetoothDisconnected();
    }

    private void onBluetoothDisconnected() {
        text_connected_.setText("Disconnected");
        connected_ = false;
        handshaked_ = false;

        connect();
    }

    private void onBluetoothConnected(BluetoothSocket s) {
        // initial connection established
        Log.i(TAG, "BLUETOOTH CONNECTED AND READY");

        text_connected_.setText("Connected");
        try {
            data_sink_ = Okio.sink(s.getOutputStream());
            //ExecutorSink es = ExecutorSink(Okio.sink(s.getOutputStream()), executor_,
            data_source_ = Okio.source(s.getInputStream());

            // start the data reader
            BackgroundReader r = new BackgroundReader();
            new Thread(r).start();
            connected_ = true;
        } catch (IOException e) {
            Log.e(TAG, "Got IOException trying to open stream: " + e.toString());
        }

        // send initial handshake message
        Log.i(TAG, "Sending handshake");
        sendHandshakeMessage();
    }



    ///////////// Sending functions
    void sendHandshakeMessage() {
        sendMessage(new BlackCoral.Builder().handshake(new Handshake(4, 40)).build(), null);
    }



    void sendMessage(BlackCoral bc, Buffer buf) {

        String bc2 = bc.toString();
        String str = "";
        if (buf != null && buf.size() > 0) {
            str = str + " payloadSize=" + buf.size();
        }
        Log.i(TAG, "Sent msg: " + str + " : " + bc.toString());
        try {
            Buffer b2 = new Buffer();
            ProtoWriter pw = new ProtoWriter(b2);
            pw.writeVarint32(bc.adapter().encodedSize(bc));
            bc.adapter().encode(pw, bc);
            if (buf != null) {
                b2.write(buf, buf.size());
            }

            sendFramedData(b2);

        } catch (IOException e) {
            Log.e(TAG, "Could not write: " + e.toString());
        }
    }


    void sendFramedData(Buffer b) throws IOException {
        Buffer b2 = new Buffer();
        long size = b.size();
        if (size <= VarInt.MAX_UVARINT32_VALUE) {
            new ProtoWriter(b2).writeVarint32((int)b.size());
            b2.writeAll(b);
            Log.i(TAG, "WRITING DATA: " + b2.size());
            data_sink_.write(b2, b2.size());
            return;
        }
        throw new IOException("Data of size " + size + " is too large");
    }



    /// Utilties for interacting w glasses
    private class GetHostTask extends AsyncTask<Void, Void, InetAddress> {
        private String host_;
        private GetHostTask(String name) {
            host_ = name;
        }

        public InetAddress doInBackground(Void... args) {
            try {
                return InetAddress.getByName(this.host_);
            } catch (UnknownHostException e) {
                Log.e(TAG, "GetHostByName failed : " + e.toString());
                return null;
            }
        }

        public void onPostExecute(InetAddress addr) {
            if (addr == null) {
                Log.i(TAG, "GetHostByName failed");
                sendMessage(new BlackCoral.Builder().getHostByNameResponse(new GetHostByNameResponse(
                        host_,
                        co.glassio.blackcoral.Status.ERROR,
                        null,
                        4)).build(), null);

            } else {
                Log.i(TAG, "Publishing GetHostByName result: name=" + host_ + " result=" + addr.getHostAddress());
                sendMessage(new BlackCoral.Builder().getHostByNameResponse(new GetHostByNameResponse(
                        host_,
                        co.glassio.blackcoral.Status.OK,
                        addr.getHostAddress(),
                        null)).build(), null);
            }
        }
    }


    ///////////// Receiving functions
    private class DataEvent {
        public final Buffer data;
        public DataEvent(Buffer buf) {
            this.data = buf;
        }
    }

    private class DisconnectedEvent {

    };

    private class BackgroundReader implements Runnable {
        public void run() {
            Log.i(TAG, "STARTING READER LOOP");
            Buffer buf = new Buffer();
            try {
                while (!MainActivity.this.stopRequested_ && MainActivity.this.data_source_.read(buf, MAX_CHUNK_SIZE) > 0) {
                    //Log.i(TAG, "GOT DATA FROM DEVICE: " + buf.size());
                    Buffer buf2 = new Buffer();
                    buf2.writeAll(buf);
                    MainActivity.this.evbus_.post(new DataEvent(buf2));
                }
                Log.i(TAG, "DONE WITH WHILE LOOP");
            } catch (IOException e) {
                Log.w(TAG, "Thread stopped due to exception: " + e.toString());
            }
            Log.i(TAG, "EXIT READER WHILE LOOP");
            MainActivity.this.evbus_.post(new DisconnectedEvent());
            //MainActivity.this.onBluetoothDisconnected();
        }
    }


    @Subscribe(threadMode = ThreadMode.MAIN)
    public void onDataReceivedFromBluetooth(DataEvent d) {
        //Log.i(TAG, "Got msg: len=" + d.data.size());

        try {
            recv_data_.writeAll(d.data);

            //Log.i(TAG, "Added to recv data: len=" + recv_data_.size());
            while (recv_data_.size() > 0) {
                //Log.i(TAG, "Processing one: pending=" + pending_frame_size_);
                if (pending_frame_size_ <= 0) {
                    try {
                        pending_frame_size_ = VarInt.readUVarInt32(recv_data_);
                    } catch (ArrayIndexOutOfBoundsException e) {
                        return;
                    } catch (IOException e) {
                        reset_recv();
                        Log.e(TAG, "Failed to read varint from recv data: " + e.toString());
                        return;
                    }
                }
                long size = recv_data_.size();
                long j = pending_frame_size_;
                if (size >= j) {
                    if (j == 0) {
                        Log.e(TAG, "Received frame with size 0");
                    } else {
                        Buffer b2 = new Buffer();
                        b2.write(recv_data_, pending_frame_size_);
                        pending_frame_size_ = 0;
                        //Log.i(TAG, "Received full frame");
                        onUnframedDataReceivedFromBluetooth(b2);
                    }
                } else {
                    return;
                }
            }
        } catch (IOException e2) {
            Log.e(TAG, "Failed to unframe data: " + e2.toString());
            reset_recv();
        }
    }

    private void onUnframedDataReceivedFromBluetooth(Buffer b) {
        try {
            int len = new ProtoReader(b).readVarint32();
            Buffer b2 = new Buffer();
            b2.write(b, (long)len);

            //Log.i(TAG, "Attempting to decode len=" + len);
            LCompanion m = LCompanion.ADAPTER.decode(
                    (BufferedSource)b2
            );
            //Log.i(TAG, "Done decode ");

            onMessageReceivedFromBluetooth(m, b);
        } catch (IOException e) {
            Log.e(TAG, "Failed to decode message: " + e.toString());
        }
    }


    int sock_state_ = 0;

    private void onMessageReceivedFromBluetooth(LCompanion m, Buffer b) {
        Log.i(TAG, "Got msg from glasses: " + m.toString());

        if (m.handshakeResponse != null) {
            Log.i(TAG, "Handshaked");

            handshaked_ = true;
        } else if (m.getHostByName != null) {
            connectTask_ = new ConnectTask(btSocket_) {
                public void onPostExecute(Boolean b) {
                    if (b.booleanValue()) {
                        MainActivity.this.onBluetoothConnected(this.socket);
                        Log.i(TAG, "Connected");
                    } else {
                        Log.e(TAG, "COULD NOT CONNECT");
                    }
                }
            };

            if (m.getHostByName.name.equals("north-teleprompter.herokuapp.com")) {
                Log.i(TAG, "Got request to getHostByName for teleprompter - handing fake address back");
                sendMessage(new BlackCoral.Builder().getHostByNameResponse(new GetHostByNameResponse(
                        m.getHostByName.name,
                        co.glassio.blackcoral.Status.OK,
                        FIXED_DUMMY_IP, //"10.0.0.148", //.1.1.1",
                        null)).build(), null);
            } else {
                Log.i(TAG, "Got request to getHostByName - looking up in bacakground: " + m.getHostByName.name);
                new GetHostTask(m.getHostByName.name).executeOnExecutor(this.executor_, new Void[0]);
            }
        } else if (m.socketOpen != null) {
            if (m.socketOpen.host.equals(FIXED_DUMMY_IP)) {
                sock_state_ = 0;
                Log.i(TAG, "Rerouting to local: " + m.socketOpen.streamId);
                ws_mgr_.onOpen(m.socketOpen.streamId);

                if (!FULL_INTERCEPT)
                    sock_mgr_.openSocket(m.socketOpen.streamId, "10.0.0.148", 8002);

                sendMessage(new BlackCoral.Builder().socketOpenResponse(new SocketOpenResponse(
                        m.socketOpen.streamId,
                        co.glassio.blackcoral.Status.OK,
                        null)).build(), null);
            } else {
                Log.i(TAG, "Calling sockmgr openSocket id=" + m.socketOpen.streamId);
                sock_mgr_.openSocket(m.socketOpen.streamId, m.socketOpen.host, m.socketOpen.port);
            }
        } else if (m.socketDataChunk != null) {

            if (ws_mgr_.shouldHandle(m.socketDataChunk.streamId)) {
                Buffer b2 = b.clone();
                ws_mgr_.onData(m.socketDataChunk.streamId, b);
                if (!FULL_INTERCEPT)
                    sock_mgr_.sendData(m.socketDataChunk.streamId, b2);

            } else {
                Buffer bc = b.clone();
                sock_mgr_.sendData(m.socketDataChunk.streamId, bc);
            }

        } else if (m.socketClose != null) {
            if (ws_mgr_.shouldHandle(m.socketClose.streamId)) {
                ws_mgr_.onClose(m.socketClose.streamId);
                sendMessage(new BlackCoral.Builder().socketCloseResponse(new SocketCloseResponse(
                        m.socketClose.streamId, Status.OK, null)).build(), null);
            }
            sock_mgr_.closeSocket(m.socketClose.streamId);
        } else if (m.socketError != null) {
            sock_mgr_.socketError(m.socketError.streamId);
        }
    }

    void reset_recv() {
        recv_data_.clear();
        pending_frame_size_ = 0;
    }

}
