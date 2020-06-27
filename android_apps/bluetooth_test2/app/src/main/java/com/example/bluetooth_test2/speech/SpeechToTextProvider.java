/*
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.example.bluetooth_test2.speech;

import android.content.Context;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;

import com.google.audio.CodecAndBitrate;
import com.google.audio.NetworkConnectionChecker;
import com.google.audio.asr.CloudSpeechSessionParams;
import com.google.audio.asr.CloudSpeechStreamObserverParams;
import com.google.audio.asr.RepeatingRecognitionSession;
import com.google.audio.asr.SafeTranscriptionResultFormatter;
import com.google.audio.asr.SpeechRecognitionModelOptions;
import com.google.audio.asr.TranscriptionResultFormatterOptions;
import com.google.audio.asr.TranscriptionResultUpdatePublisher;
import com.google.audio.asr.TranscriptionResultUpdatePublisher.ResultSource;
import com.google.audio.asr.cloud.CloudSpeechSessionFactory;
import com.google.protobuf.Duration;

import static com.google.audio.asr.SpeechRecognitionModelOptions.SpecificModel.DICTATION_DEFAULT;
import static com.google.audio.asr.SpeechRecognitionModelOptions.SpecificModel.VIDEO;
import static com.google.audio.asr.TranscriptionResultFormatterOptions.TranscriptColoringStyle.NO_COLORING;

public class SpeechToTextProvider {
    private static final int PERMISSIONS_REQUEST_RECORD_AUDIO = 1;

    private static final int MIC_CHANNELS = AudioFormat.CHANNEL_IN_MONO;
    private static final int MIC_CHANNEL_ENCODING = AudioFormat.ENCODING_PCM_16BIT;
    private static final int MIC_SOURCE = MediaRecorder.AudioSource.VOICE_RECOGNITION;
    //private static final int MIC_SOURCE = MediaRecorder.AudioSource.CAMCORDER;
    private static final int SAMPLE_RATE = 16000;
    private static final int CHUNK_SIZE_SAMPLES = 1280;
    private static final int BYTES_PER_SAMPLE = 2;

    private static final String API_KEY = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"; // replaced for push to github
    private static final String SHARE_PREF_API_KEY = "api_key";

    private int currentLanguageCodePosition;
    private String currentLanguageCode;

    private AudioRecord audioRecord;
    private final byte[] buffer = new byte[BYTES_PER_SAMPLE * CHUNK_SIZE_SAMPLES];

    // This class was intended to be used from a thread where timing is not critical (i.e. do not
    // call this in a system audio callback). Network calls will be made during all of the functions
    // that RepeatingRecognitionSession inherits from SampleProcessorInterface.
    private RepeatingRecognitionSession recognizer;
    private NetworkConnectionChecker networkChecker;
    private Context context;

    private SpeechListener listener_;

    boolean inited_ = false;

    public void setListener(SpeechListener l) { listener_ = l; }


    private final TranscriptionResultUpdatePublisher transcriptUpdater =
            (formattedTranscript, updateType) -> {
                if (listener_ != null) {
                    if (updateType != TranscriptionResultUpdatePublisher.UpdateType.TRANSCRIPT_FINALIZED) {
                        if (listener_.onSpeech(formattedTranscript.toString()))
                        {
                            recognizer.resetAndClearTranscript();
                        }
                    }
                }
            };

    private Runnable readMicData =
            () -> {
                if (audioRecord.getState() != AudioRecord.STATE_INITIALIZED) {
                    return;
                }
                recognizer.init(CHUNK_SIZE_SAMPLES);
                while (audioRecord.getRecordingState() == AudioRecord.RECORDSTATE_RECORDING) {
                    audioRecord.read(buffer, 0, CHUNK_SIZE_SAMPLES * BYTES_PER_SAMPLE);
                    recognizer.processAudioBytes(buffer);
                }
                recognizer.stop();
            };


    public SpeechToTextProvider(Context c) {
        context = c;
        initLanguageLocale();
    }

    public void start() {
        constructRepeatingRecognitionSession();
        startRecording();
    }

    public void stop() {
        audioRecord.stop();
    }

    public void shutdown() {
       // final shutdown call

        if (recognizer != null) {
            recognizer.unregisterCallback(transcriptUpdater);
            networkChecker.unregisterNetworkCallback();
        }
    }


    private void initLanguageLocale() {
        // The default locale is en-US.
        currentLanguageCode = "en-US";
        currentLanguageCodePosition = 22;
    }

    private void constructRepeatingRecognitionSession() {
        if (inited_)
            return;

        inited_ = true;
        SpeechRecognitionModelOptions options =
                SpeechRecognitionModelOptions.newBuilder()
                        .setLocale(currentLanguageCode)
                        // As of 7/18/19, Cloud Speech's video model supports en-US only.
                        .setModel(currentLanguageCode.equals("en-US") ? VIDEO : DICTATION_DEFAULT)
                        .build();
        CloudSpeechSessionParams cloudParams =
                CloudSpeechSessionParams.newBuilder()
                        .setObserverParams(
                                CloudSpeechStreamObserverParams.newBuilder().setRejectUnstableHypotheses(false))
                        .setFilterProfanity(true)
                        .setEncoderParams(
                                CloudSpeechSessionParams.EncoderParams.newBuilder()
                                        .setEnableEncoder(true)
                                        .setAllowVbr(true)
                                        .setCodec(CodecAndBitrate.OGG_OPUS_BITRATE_32KBPS))
                        .build();
        networkChecker = new NetworkConnectionChecker(context);
        networkChecker.registerNetworkCallback();

        // There are lots of options for formatting the text. These can be useful for debugging
        // and visualization, but it increases the effort of reading the transcripts.
        Duration d = Duration.newBuilder().setNanos(500*1000*1000).build();

        TranscriptionResultFormatterOptions formatterOptions =
                TranscriptionResultFormatterOptions.newBuilder()
                        .setExtendedSilenceDurationForLineBreaks(d)
                        .setTranscriptColoringStyle(NO_COLORING)
                        .build();
        RepeatingRecognitionSession.Builder recognizerBuilder =
                RepeatingRecognitionSession.newBuilder()
                        .setSpeechSessionFactory(new CloudSpeechSessionFactory(cloudParams, SpeechToTextProvider.getApiKey(context)))
                        .setSampleRateHz(SAMPLE_RATE)
                        .setTranscriptionResultFormatter(new SafeTranscriptionResultFormatter(formatterOptions))
                        .setSpeechRecognitionModelOptions(options)
                        .setNetworkConnectionChecker(networkChecker);
        recognizer = recognizerBuilder.build();
        //recognizer.registerCallback(transcriptUpdater, ResultSource.WHOLE_RESULT);
        recognizer.registerCallback(transcriptUpdater, ResultSource.MOST_RECENT_SEGMENT);
    }

    private void startRecording() {
        if (audioRecord == null) {
            audioRecord =
                    new AudioRecord(
                            MIC_SOURCE,
                            SAMPLE_RATE,
                            MIC_CHANNELS,
                            MIC_CHANNEL_ENCODING,
                            CHUNK_SIZE_SAMPLES * BYTES_PER_SAMPLE);
        }

        audioRecord.startRecording();
        new Thread(readMicData).start();
    }


    /** Saves the API Key in user shared preference. */
    private static void saveApiKey(Context context, String key) {
        //PreferenceManager.getDefaultSharedPreferences(context)
        //        .edit()
        //        .putString(SHARE_PREF_API_KEY, key)
        //        .commit();
    }

    /** Gets the API key from shared preference. */
    private static String getApiKey(Context context) {
        return API_KEY;
        //return PreferenceManager.getDefaultSharedPreferences(context).getString(SHARE_PREF_API_KEY, "");
    }
}
