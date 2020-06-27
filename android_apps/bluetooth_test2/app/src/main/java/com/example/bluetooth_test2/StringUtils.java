package com.example.bluetooth_test2;

import java.io.EOFException;
import java.text.Format;
import java.util.Formatter;

import okio.Buffer;

public class StringUtils {
    public static String getHexValues(Buffer s) {
        Buffer b2 = s.clone();

        Formatter f = new Formatter();
        try {
            for (int i = 0; i < b2.size(); ++i) {
                //int x = b2.readByte();

                f.format(",%02x", b2.readByte());
                //s2 = s2 + "," + x;
            }
        } catch (EOFException e) {
        }
        String s2 = f.toString();
        f.close();
        return s2;
    }
}
