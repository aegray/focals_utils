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

public class AnkiCardPresentationProvider extends PresentationProvider {
    private static final String TAG = "AnkiCardPresentationProvider";

    int state_ = 0;

    int question_state_ = 0;

    AnkiCardLayer cards_;
    AnkiCardLayer.Card next_card_;

    IPresenter presenter_;
    long card_start_time_ = 0;

    boolean inited_ = false;

    public AnkiCardPresentationProvider(MainActivity c) {
        cards_ = new AnkiCardLayer(c);

        if (cards_.requestPerms(c, 0)) {
            checkCards();
        }
    }

    public void checkCards() {
        try {
            cards_.queryForDeckNames();
            inited_ = true;
        } catch (IllegalArgumentException e) {
            Log.e(TAG, "Failed to query card: " + e.toString());
        }
    }

    public void gotPermissions() {
        checkCards();
    }

    public void lookupDecks() {
        checkCards();
        next_card_ = cards_.getNextCard();
    }

    public void getNextCard() {
        if (!inited_) {
            checkCards();
        }
        next_card_ = cards_.getNextCard();
        card_start_time_ = System.currentTimeMillis();
    }

    void sendNextCard() {
        getNextCard();

        if(next_card_ == null)
        {
            presenter_.sendCard("No cards left");
        }
        else
        {
            Log.d(TAG, "Sending card question: " + next_card_.question);
            String[] sp = next_card_.question.split("</");
            if (sp.length > 1) {
                String[] sp2 = sp[0].split(">");
                if (sp2.length > 1) {
                    presenter_.sendCard(" \n \n \n" + "_________  " + sp2[1]);
                }

            } else {
                Log.d(TAG, "Sending card question: " + next_card_.question);
                //writeCardData("TESTING2");
                presenter_.sendCard("____ " + next_card_.question);
            }
        }
    }

    void sendAnswer() {
        if (next_card_ == null) {
            presenter_.sendCard("No cards left");
        } else {
            Log.d(TAG, "Sending card answer: " + next_card_.answer);
            presenter_.sendCard(next_card_.answer);
        }
    }


    @Override
    public void resetPresentation() {
        state_ = 2;
        sendNextCard();
    }

    @Override
    public void onNext() {
        if (state_ == 2) {
            state_ = 3;
            sendAnswer();
        } else if (state_ == 3) {
            cards_.respondCardEase(next_card_, true);
            state_ = 2;
            sendNextCard();
        }
    }

    @Override
    public void onPrevious() {
        if (state_ == 3) {
            cards_.respondCardEase(next_card_, false);
            state_ = 2;
            sendNextCard();
        }
    }


    @Override
    public void setPresenter(IPresenter p) {
        presenter_ = p;
    }
}
