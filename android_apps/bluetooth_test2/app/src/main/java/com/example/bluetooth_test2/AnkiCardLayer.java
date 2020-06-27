package com.example.bluetooth_test2;


import android.app.Activity;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Context;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.net.Uri;
import android.util.Log;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.ichi2.anki.FlashCardsContract;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import co.glassio.blackcoral.ActivityState;

import static com.ichi2.anki.api.AddContentApi.READ_WRITE_PERMISSION;


public class AnkiCardLayer {
    private static final Uri DUE_CARD_REVIEW_INFO_URI = FlashCardsContract.ReviewInfo.CONTENT_URI;
    private static final String TAG = "AnkiCardLayer";
    private Context context_;
    public static final String[] SIMPLE_CARD_PROJECTION = {
            FlashCardsContract.Card.ANSWER_PURE,
            FlashCardsContract.Card.QUESTION_SIMPLE};

    private long deck_id_ = 0;

    private static final String DESIRED_DECK_NAME = "Mandarin: Vocabulary::a. HSK";

    class Card {
        long start_time;
        long note_id;
        int card_ord;
        String question;
        String answer;

        public Card(long _starttime, long _note_id, int _card_ord, String q, String a) {
            start_time = _starttime;
            note_id = _note_id;
            card_ord = _card_ord;
            question = q;
            answer = a;
        }
    }

    public AnkiCardLayer(Context c) {
        context_ = c;
    }

    public boolean requestPerms(Activity callback, int callbackCode) {
        if (ContextCompat.checkSelfPermission(context_, READ_WRITE_PERMISSION) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(callback, new String[]{ READ_WRITE_PERMISSION }, callbackCode);
            return false;
        }
        return true;
    }

    public Card getNextCard() {
        if (deck_id_ != 0) { return queryForCurrentCard(deck_id_); }
        return null;
    }


    void respondCardEase(Card c, boolean was_easy) {
        int ease = was_easy ? 2 : 1;

        long timeTaken = System.currentTimeMillis() - c.start_time;
        ContentResolver cr = context_.getContentResolver();
        Uri reviewInfoUri = FlashCardsContract.ReviewInfo.CONTENT_URI;
        ContentValues values = new ContentValues();
        values.put(FlashCardsContract.ReviewInfo.NOTE_ID, c.note_id);
        values.put(FlashCardsContract.ReviewInfo.CARD_ORD, c.card_ord);
        values.put(FlashCardsContract.ReviewInfo.EASE, ease);
        values.put(FlashCardsContract.ReviewInfo.TIME_TAKEN, timeTaken);
        Log.d(TAG, timeTaken + " time taken " + values.getAsLong(FlashCardsContract.ReviewInfo.TIME_TAKEN));
        cr.update(reviewInfoUri, values, null, null);
    }



    public Card queryForCurrentCard(long deckID) {
        //Log.d(TAG, "WearMessageListenerService: queryForCurrentCard");
        String deckArguments[] = new String[deckID == 0 ? 1 : 2];
        String deckSelector = "limit=?";
        deckArguments[0] = "" + 1;
        if (deckID != -1) {
            deckSelector += ",deckID=?";
            deckArguments[1] = "" + deckID;
        }

        Cursor reviewInfoCursor = context_.getContentResolver().query(DUE_CARD_REVIEW_INFO_URI, null, deckSelector, deckArguments, null);

        if (reviewInfoCursor == null || !reviewInfoCursor.moveToFirst()) {
            Log.d(TAG, "query for due card info returned no result");
            //sendNoMoreCardsToWear();
            if (reviewInfoCursor != null) {
                reviewInfoCursor.close();
            }
        } else {
            //cardQueue.clear();
            do {
                //CardInfo card = new CardInfo();

                int cardOrd = reviewInfoCursor.getInt(reviewInfoCursor.getColumnIndex(FlashCardsContract.ReviewInfo.CARD_ORD));
                long noteID = reviewInfoCursor.getLong(reviewInfoCursor.getColumnIndex(FlashCardsContract.ReviewInfo.NOTE_ID));
                int buttonCount = reviewInfoCursor.getInt(reviewInfoCursor.getColumnIndex(FlashCardsContract.ReviewInfo.BUTTON_COUNT));

                Uri noteUri = Uri.withAppendedPath(FlashCardsContract.Note.CONTENT_URI, Long.toString(noteID));
                Uri cardsUri = Uri.withAppendedPath(noteUri, "cards");
                Uri specificCardUri = Uri.withAppendedPath(cardsUri, Integer.toString(cardOrd));
                final Cursor specificCardCursor = context_.getContentResolver().query(specificCardUri,
                            SIMPLE_CARD_PROJECTION,  // projection
                            null,  // selection is ignored for this URI
                            null,  // selectionArgs is ignored for this URI
                            null   // sortOrder is ignored for this URI
                    );
                if (specificCardCursor == null || !specificCardCursor.moveToFirst()) {
                    Log.d(TAG, "query for due card info returned no result");
                    //sendNoMoreCardsToWear();
                    //if (specificCardCursor != null) {
                     //   specificCardCursor.close();
                    //}
                    reviewInfoCursor.close();
                    return null;
                } else {
                    String answer = specificCardCursor.getString(specificCardCursor.getColumnIndex(FlashCardsContract.Card.ANSWER_PURE));
                    String question = specificCardCursor.getString(specificCardCursor.getColumnIndex(FlashCardsContract.Card.QUESTION_SIMPLE));
                    specificCardCursor.close();

                    String[] qparts = question.split("<hr>");
                    String[] aparts = answer.split("<hr>");

                    reviewInfoCursor.close();
                    return new Card(System.currentTimeMillis(), noteID, cardOrd, qparts[0], aparts[0]);

                    //Log.d(TAG, "Got card: " + cardOrd + " / " + noteID + "/" + buttonCount + " q=" + question + " : a=" + answer); //+ "/" + nextReviewTexts);
                }

               // try {
               // //    card.fileNames = new JSONArray(reviewInfoCursor.getString(reviewInfoCursor.getColumnIndex(FlashCardsContract.ReviewInfo.MEDIA_FILES)));
               //     card.nextReviewTexts = new JSONArray(reviewInfoCursor.getString(reviewInfoCursor.getColumnIndex(FlashCardsContract.ReviewInfo.NEXT_REVIEW_TIMES)));
               // } catch (JSONException e) {
               //    e.printStackTrace();
               // }


                //Log.v(TAG, "card added to queue: " + card.fileNames);

                //new GrabAndProcessFilesTask().execute(card);

                //cardQueue.add(card);


            } while (reviewInfoCursor.moveToNext());

           // reviewInfoCursor.close();

//
//            if (cardQueue.size() >= 1) {
//
//                for (CardInfo card : cardQueue) {
//                    Uri noteUri = Uri.withAppendedPath(FlashCardsContract.Note.CONTENT_URI, Long.toString(card.noteID));
//                    Uri cardsUri = Uri.withAppendedPath(noteUri, "cards");
//                    Uri specificCardUri = Uri.withAppendedPath(cardsUri, Integer.toString(card.cardOrd));
//                    final Cursor specificCardCursor = getContentResolver().query(specificCardUri,
//                            SIMPLE_CARD_PROJECTION,  // projection
//                            null,  // selection is ignored for this URI
//                            null,  // selectionArgs is ignored for this URI
//                            null   // sortOrder is ignored for this URI
//                    );
//
//                    if (specificCardCursor == null || !specificCardCursor.moveToFirst()) {
//                        Log.d(TAG, "query for due card info returned no result");
//                        sendNoMoreCardsToWear();
//                        if (specificCardCursor != null) {
//                            specificCardCursor.close();
//                        }
//                        return;
//                    } else {
//                        card.a = specificCardCursor.getString(specificCardCursor.getColumnIndex(FlashCardsContract.Card.ANSWER_PURE));
//                        card.q = specificCardCursor.getString(specificCardCursor.getColumnIndex(FlashCardsContract.Card.QUESTION_SIMPLE));
//                        specificCardCursor.close();
//                    }
//                }
//
//                CardInfo nextCard = cardQueue.get(0);
//                cardStartTime = System.currentTimeMillis();
//                sendCardToWear(nextCard.q, nextCard.a, nextCard.nextReviewTexts, nextCard.noteID, nextCard.cardOrd);
//            }
        }
        return null;

    }

    public void queryForDeckNames() {

        // query for current card (based on deck id)

        // get deck id


        // choose collection

        // respond card ease


        Cursor deckCursor = context_.getContentResolver().query(FlashCardsContract.Deck.CONTENT_ALL_URI, FlashCardsContract.Deck.DEFAULT_PROJECTION, null, null, null);
        if (deckCursor == null) {
            Log.e(TAG, "Can't query decks");
            return;
        }

        if (!deckCursor.moveToFirst()) {
            Log.e(TAG, "Query for decks found no results");
            deckCursor.close();
        } else {
            do {
                long did = deckCursor.getLong(deckCursor.getColumnIndex(FlashCardsContract.Deck.DECK_ID));
                String deckname = deckCursor.getString(deckCursor.getColumnIndex(FlashCardsContract.Deck.DECK_NAME));

                if (deckname.startsWith(DESIRED_DECK_NAME)) {
                    deck_id_ = did;
                    Log.d(TAG, "Got deck: " + did + " name=" + deckname);
                } else {

                    Log.d(TAG, "NOn selected deck: " + did + " name=" + deckname);
                }
                // try {
               //     JSONObject deckOptions = new JSONObject(deckCursor.getString(deckCursor.getColumnIndex(FlashCardsContract.Deck.OPTIONS)));
               //     JSONArray deckCounts = new JSONArray(deckCursor.getString(deckCursor.getColumnIndex(FlashCardsContract.Deck.DECK_COUNTS)));
               //     Log.d(TAG, "deckCounts " + deckCounts);
               //     Log.d(TAG, "deck Options " + deckOptions);
               //     //decks.put(deckName, deckID);
               // } catch (JSONException e) {
               //     e.printStackTrace();
               // }
            } while (deckCursor.moveToNext());
        }
    }



}
