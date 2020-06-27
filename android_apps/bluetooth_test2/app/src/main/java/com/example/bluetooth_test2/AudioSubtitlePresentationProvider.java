package com.example.bluetooth_test2;

import android.content.Context;
import android.util.Log;

import com.example.bluetooth_test2.speech.SpeechListener;
import com.example.bluetooth_test2.speech.SpeechToTextProvider;

public class AudioSubtitlePresentationProvider extends PresentationProvider implements SpeechListener {
    private static final String TAG = "StreamingTextPresentationProvider";
    private static final int RESET_AFTER_MILLIS = 1000;
    private Context context_;
    private SpeechToTextProvider speech_;

    private static final int MAX_CHARS_ON_SCREEN = 60;

    private String prev_;
    private String last_full_;

    boolean open_ = false;


    private long last_speech_ = 0;

    IPresenter presenter_;
    String str_ = "";


    AudioSubtitlePresentationProvider(Context c) {

        speech_ = new SpeechToTextProvider(c);
        speech_.setListener(this);
    }

    ///// droid speech shit

    Runnable periodic_clearer = new Runnable() {
        @Override
        public void run() {

            if (open_) {
                long cur = System.currentTimeMillis();
                if (cur > last_speech_ + RESET_AFTER_MILLIS) {
                    prev_ = last_full_;
                    presenter_.sendCard(""); //result.substring(result.length() - MAX_CHARS_ON_SCREEN));
                }

                new android.os.Handler().postDelayed(this, 500);
            }
        }
    };


    @Override
    public void resetPresentation() {
        str_ = "";
        open_ = true;
        presenter_.sendCard("");
        speech_.start();

        last_speech_ = System.currentTimeMillis();
        new android.os.Handler().postDelayed(periodic_clearer, 500);

        Log.i(TAG, "Starting to listen for speech audio");
    }

    @Override
    public void onNext() {
    }

    @Override
    public void onPrevious() {
    }

    @Override
    public void onClose() {
        open_ = false;
        speech_.stop();
    }

    @Override
    public void setPresenter(IPresenter p) {
        presenter_ = p;
    }



    @Override
    public boolean onSpeech(String iresult) {
        if (open_) {
            last_speech_ = System.currentTimeMillis();
            last_full_ = iresult;
            String[] parts = iresult.split("\n");
            iresult = parts[parts.length-1];

            if (prev_ != null) {
                if ((iresult.length() < prev_.length()) && (iresult.length() < MAX_CHARS_ON_SCREEN / 2)) {
                    prev_ = null;
                }
            }

            String result = iresult;
            if ((prev_ != null)  && (result.length() > prev_.length())) {
                result = result.substring(prev_.length());
            }

            if (result.length() > MAX_CHARS_ON_SCREEN) {
                int index = iresult.lastIndexOf(' ');

                if (index >= 0)
                    prev_ = iresult.substring(0, index+1);
                else
                    prev_ = iresult;

                presenter_.sendCard(result); //result.substring(result.length() - MAX_CHARS_ON_SCREEN));
                Log.i(TAG, "Sending text: " + result.length() + " / " + result + " / " + prev_);
                return false;
            } else {
                presenter_.sendCard(result);
                return false;
            }
        }
        return false;
    }
}
