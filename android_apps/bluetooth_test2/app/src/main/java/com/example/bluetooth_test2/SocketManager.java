package com.example.bluetooth_test2;

import android.os.AsyncTask;
import android.util.Log;

import org.greenrobot.eventbus.EventBus;
import org.greenrobot.eventbus.Subscribe;
import org.greenrobot.eventbus.ThreadMode;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Executor;

import okio.Buffer;
import okio.Okio;
import okio.Sink;
import okio.Source;

public class SocketManager {

    /// consts
    private static final long MAX_DATA_CHUNK_SIZE = 950;
    private static final String TAG = "SocketManager";
    private final Map<Integer, SocketHolder> sockets_ = new HashMap();


    /// Privates
    private Executor executor_;
    private EventBus event_bus = new EventBus();

    static class ISocketManagerListener {
        public void onSocketOpenResult(int id, boolean success, int error_code) { }
        public void onSocketError(int id, int error_code) { }
        public void onSocketData(int id, Buffer data) { }
        public void onSocketCloseResult(int id, boolean success, int error_code) { }
    }
    private ISocketManagerListener listener_;
    public void setListener(ISocketManagerListener l) { listener_ = l; }


    class SocketHolder {
        private final Socket socket_;
        public final int stream_id;
        private final Executor executor_;

        private Source data_source_;
        private Sink data_sink_;

        private BackgroundReader reader_;


        private class DataEvent {
            public int id;
            public final Buffer data;
            public DataEvent(int id, Buffer buf) {
                this.id = id;
                this.data = buf;
            }
        }

        private class BackgroundReader implements Runnable {
            private boolean stop_requested_ = false;
            public void run() {
                Buffer buf = new Buffer();
                try {
                    while (!stop_requested_ && data_source_.read(buf, MAX_DATA_CHUNK_SIZE) > 0) {
                        Buffer buf2 = new Buffer();
                        buf2.writeAll(buf);
                        event_bus.post(new DataEvent(stream_id, buf2));
                    }
                    Log.i(TAG, "DONE WITH WHILE LOOP");
                } catch (IOException e) {
                    Log.w(TAG, "Thread stopped due to exception: " + e.toString());
                }
                Log.i(TAG, "EXIT READER WHILE LOOP");
            }

            public void requestStop() {
                stop_requested_ = true;
            }
        }

        public class ConnectTask extends AsyncTask<Void, Void, Boolean> {
            private String host;
            private int port;

            private ConnectTask(String h, int p) {
                host = h;
                port = p;
            }

            public Boolean doInBackground(Void... args) {
                try {
                    try {
                        SocketHolder.this.socket_.connect(
                                new InetSocketAddress(host, port)
                        );
                        return true;
                    } catch (IOException | IllegalArgumentException e) {
                        Log.e(TAG, "Failed creating connecting socket for " + host + ":" + port);
                    }

                } catch (IllegalArgumentException e2) {
                    Log.e(TAG, "Failed creating connecting socket (ilarg) for " + host + ":" + port);
                }
                return false;
            }

            public void onPostExecute(Boolean b) {
                if (b.booleanValue()) {
                    SocketHolder.this.onSocketOpened();
                } else {
                    SocketHolder.this.onSocketOpenFailed();
                }
            }
        }


        public SocketHolder(int id, Executor executor) {
            stream_id = id;
            socket_ = new Socket();
            executor_ = executor;
        }

        public void writeData(Buffer d) {
            final Buffer b2 = new Buffer();
            b2.write(d, d.size());
            executor_.execute(new Runnable() {
                final Buffer buf;
                {
                   buf = b2;
                }

                @Override
                public void run() {
                    try {
                        data_sink_.write(buf, buf.size());
                    } catch (IOException e) {
                        Log.e(TAG, "Failed to write to socket: " + e.toString());
                    }
                }
            });
            //try {
            //    data_sink_.write(d, d.size());
            //} catch (IOException e) {
            //    Log.e(TAG, "Failed to write socket data: stream_id=" + stream_id);
            //}
        }

        public void open(String address, int port) {
            new ConnectTask(address, port).executeOnExecutor(executor_, new Void[0]);
        }

        public void close() {
            if (reader_ != null) {
                reader_.requestStop();
            }

            if (data_source_ != null) {
                try {
                    data_source_.close();
                } catch (IOException e) { }

                data_source_ = null;
            }

            data_sink_ = null;
        }

        public void onSocketOpened() {
            try {
                data_sink_ = Okio.sink(socket_.getOutputStream());
                data_source_ = Okio.source(socket_.getInputStream());
            } catch (IOException e) {
                SocketManager.this.onSocketOpenFailed(this);
                try {
                    socket_.close();
                } catch (IOException e2) {

                }
                data_sink_ = null;
                data_source_ = null;
                return;
            }

            reader_ = new BackgroundReader();
            new Thread(reader_).start();
            SocketManager.this.onSocketOpened(this);
        }
        public void onSocketOpenFailed() {
            SocketManager.this.onSocketOpenFailed(this);
        }

    } // end SocketHolder


    //// cons
    public SocketManager(Executor exec) {
        executor_ = exec;
        event_bus.register(this);
    }





    ///// Controls for socket
    public void openSocket(int id, String address, int port) {
        if (sockets_.containsKey(id)) {
            if (listener_ != null)
                listener_.onSocketOpenResult(id, false, 106);
            return;
        }

        SocketHolder s = new SocketHolder(id, executor_);
        s.open(address, port);
        sockets_.put(id, s);
    }

    public void closeSocket(int id) {
        SocketHolder s = sockets_.get(id);
        if (s == null) {
            if (listener_ != null)
                listener_.onSocketCloseResult(id, false, 106);
            return;
        }
        s.close();
        if (listener_ != null)
            listener_.onSocketError(s.stream_id, 104);

        cleanupSocket(id);
    }

    public void socketError(int id) {
        SocketHolder s = sockets_.get(id);
        if (s != null) {
            s.close();
            cleanupSocket(id);
        }
    }

    public void sendData(int id, Buffer data) {
        SocketHolder s = sockets_.get(id);
        if (s == null) {
            if (listener_ != null)
                listener_.onSocketError(id, 107);
        } else {
            s.writeData(data);
        }
    }


    //// Callbacks from socket holder
    @Subscribe(threadMode = ThreadMode.MAIN)
    public void onSocketData(SocketHolder.DataEvent d) {
        if (listener_ == null) return;
        // check if it's still in the map
        if (sockets_.containsKey(d.id)) {
            listener_.onSocketData(d.id, d.data);
        } else {
            listener_.onSocketError(d.id, 107);
        }
    }

    public void onSocketOpened(SocketHolder s) {
        if (listener_ == null) return;
        listener_.onSocketOpenResult(s.stream_id, true, 0);
    }

    public void onSocketClosed(SocketHolder s) {
        if (listener_ == null) return;

        if (sockets_.containsKey(s.stream_id)) {
            cleanupSocket(s.stream_id);
            listener_.onSocketError(s.stream_id, 104);
        } else {
            listener_.onSocketCloseResult(s.stream_id, true, 0);
        }
    }

    public void onSocketOpenFailed(SocketHolder s) {
        cleanupSocket(s.stream_id);
        listener_.onSocketOpenResult(s.stream_id, false, 101);
    }

    private void cleanupSocket(int id) {
        sockets_.remove(id);
    }

}
