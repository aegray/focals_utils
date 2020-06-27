package com.example.bluetooth_test2;

import android.util.Base64;
import android.util.Log;

import org.apache.commons.text.StringEscapeUtils;

import java.io.EOFException;
import java.nio.charset.Charset;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import co.glassio.blackcoral.BlackCoral;
import co.glassio.blackcoral.SocketCloseResponse;
import co.glassio.blackcoral.SocketDataChunk;
import co.glassio.blackcoral.SocketOpenResponse;
import co.glassio.blackcoral.Status;
import okio.Buffer;

import static java.nio.charset.StandardCharsets.UTF_8;

public class PresentWebsocketManager implements IPresenter {

    public static final String TAG = "WSPRESENT";
    private static final String WS_UUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";

    int state_ = 0;
    int stream_id_ = -1;

    PresentationProvider provider_;

    public static class IListener {
        public void onMessage(BlackCoral bc, Buffer b) {
        }
    }

    IListener listener_;


    public void setPresentationProvider(PresentationProvider p) {
        provider_ = p;
    }

    public void setListener(IListener l) {
        listener_ = l;
    }

    public PresentationProvider getPresentationProvider() {
        return provider_;
    }

    public boolean shouldHandle(int streamid) {
        return (stream_id_ == streamid) && (state_ != 0);
    }


    public boolean isOpen() { return stream_id_ >= 0; }

    void onOpen(int id) {
        stream_id_ = id;
        state_ = 1;
      //  if (listener_ != null)
      //      listener_.onMessage(new BlackCoral.Builder().socketOpenResponse(new SocketOpenResponse(
      //              id,
      //              co.glassio.blackcoral.Status.OK,
      //              null)).build(), null);

    }

    void onClose(int id) {
        stream_id_ = -1;
        provider_.onClose();
      //  if (stream_id_ == id) {
      //      if (listener_ != null) {
      //          listener_.onMessage(new BlackCoral.Builder().socketCloseResponse(
      //                  new SocketCloseResponse(id, Status.OK, null)).build(), null);
      //      }
      //  }
    }


    String getPacketData(Buffer b) {
        try {

            int h0 = b.readByte();
            int h1 = b.readByte();

            if ((h1 & 0x80) != 0x80) {
                Log.e(TAG, "Expected to have a mask on input data, but missing");
                return null;
            }

            int len = h1 & 0x7f;
            if (len == 126) {
                len = b.readShort();
            } else if (len == 127) {
                Log.e(TAG, "Not handling too large message from phone");
                return null;
            }

            byte[] mask_bits = new byte[4];
            for (int i = 0; i < 4; ++i) {
                mask_bits[i] = b.readByte();
            }

            Buffer res = new Buffer();
            int onind = 0;
            for (int i = 0; i < len; ++i) {
                byte c = b.readByte();
                res.writeByte(c ^ mask_bits[onind]);
                onind += 1;
                if (onind > 3) onind = 0;
            }
            return res.readString(Charset.defaultCharset());
        } catch (EOFException e) {
            Log.e(TAG, "EOF when trying to decode data from phone");
        }
        return null;
    }


    // send functions
    void writeRawData(Buffer b) {
        if (listener_ != null)
            listener_.onMessage(new BlackCoral.Builder().socketDataChunk(
                    new SocketDataChunk(stream_id_)).build(), b);
    }

    void writeData(String data) {
        Buffer bout = new Buffer();

        if (data.length() < 126) {
            bout.writeByte(0x81);
            bout.writeByte(data.length());
            bout.write(data.getBytes());
        } else if (data.length() < 65536) {
            bout.writeByte(0x81);
            bout.writeByte(126);
            short s = (short) data.length();
            bout.writeShort(s);

            bout.write(data.getBytes());
        } else {
            Log.e(TAG, "Couldn't send message - too long: " + data.length());
        }


        Log.d(TAG, "Sending ws data raw to glasses: " + bout.size() + ": " + bout.clone().readString(UTF_8)); //StringUtils.getHexValues(bout.clone()));

        if (listener_ != null)
            listener_.onMessage(new BlackCoral.Builder().socketDataChunk(
                    new SocketDataChunk(stream_id_)).build(), bout);
    }

    void writeCardData(String data) {
        writeData("{\"type\": \"current_state\", \"state\": \"currently_presenting\", \"title\": \"stuff\", \"notes\": \"" + StringEscapeUtils.escapeJava(data) + "\", \"slide_number\": -1, \"total_slides\": 3}");
    }

    @Override
    public void sendCard(String data) {
        writeCardData(data);
    }


    void onData(int id, Buffer d) {
        if (id != stream_id_) return;

        if (state_ == 1) {
            // send back HTTP websocket accept stuff
            String s = d.readString(Charset.defaultCharset());
            String[] parts = s.split("\r\n");

            String key = null;
            for (String a : parts) {
                if (a.startsWith("Sec-WebSocket-Key: ")) {
                    key = a.substring("Sec-WebSocket-Key: ".length());
                }
            }

            if (key == null) {
                Log.e(TAG, "Didn't find websocket key");
                return;
            }

            MessageDigest md;
            try {
                md = MessageDigest.getInstance("SHA-1");
            } catch (NoSuchAlgorithmException e) {
                Log.e(TAG, "Could not get sha1 provider: " + e.toString());
                return;
            }
            byte[] respkey = md.digest((key + WS_UUID).getBytes());

            String srespkey = Base64.encodeToString(respkey, Base64.NO_WRAP);

            Buffer bout = new Buffer();
            bout.writeString("HTTP/1.1 101 Switching Protocols", Charset.defaultCharset());
            bout.writeByte(13); bout.writeByte(10);
            bout.writeString("Upgrade: websocket", Charset.defaultCharset());
            bout.writeByte(13); bout.writeByte(10);
            bout.writeString("Connection: Upgrade", Charset.defaultCharset());
            bout.writeByte(13); bout.writeByte(10);
            bout.writeString("Sec-WebSocket-Accept: " + srespkey, Charset.defaultCharset());
            bout.writeByte(13); bout.writeByte(10);
            bout.writeByte(13); bout.writeByte(10);

            //Log.i(TAG, "Using websocket keys: in=" + key + " out=" + srespkey);

            writeRawData(bout);

            provider_.resetPresentation();

            writeData("{\"type\": \"connected\"}");

            state_ = 2;
        } else if (state_ == 2) {
            String s = getPacketData(d);
            Log.i(TAG, "Got data from phone: " + s);

            if (s.contains("next_slide")) {
                provider_.onNext();
            } else if (s.contains("previous_slide")) {
                provider_.onPrevious();
            }
        }
    }

}
