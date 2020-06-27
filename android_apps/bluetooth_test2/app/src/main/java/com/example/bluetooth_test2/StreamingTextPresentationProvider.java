package com.example.bluetooth_test2;

import android.util.Log;

public class StreamingTextPresentationProvider extends PresentationProvider {
    private static final String TAG = "StreamingTextPresentationProvider";
    int state_ = -1;


    int rate_ = 1000;

    String texts_[] = new String[]{
            "Sometimes you have to go",
            "To the store many times",
            "in order to find what you want",
            "and sometimes you never find it",
            "no matter how many times you go"
    };

    IPresenter presenter_;


    void sendNextCard() {
        if (state_ >= 0) {
            state_ = state_ + 1;
            if (state_ > texts_.length) {
                state_ = 1;
            }
            presenter_.sendCard(texts_[state_ - 1]);

            new android.os.Handler().postDelayed(
                    new Runnable() {
                        public void run() {
                            sendNextCard();
                            //Log.i("tag","A Kiss after 5 seconds");
                        }
                    }, rate_);
        }
    }

    @Override
    public void resetPresentation() {
        state_ = 0;
        sendNextCard();
    }

    @Override
    public void onNext() {
        rate_ = java.lang.Math.max(50, (rate_ / 2));
    }

    @Override
    public void onPrevious() {
        rate_ = rate_ * 2;
    }

    @Override
    public void onClose() {
        state_ = -1;
    }

    @Override
    public void setPresenter(IPresenter p) {
        presenter_ = p;
    }
}
