#!/bin/bash




export ANDROID_TARGET_ARCH=armeabi

./configure --prefix=/system/ \
        --extprefix=./install \
        -android-ndk $NDK_ROOT \
        -android-arch armeabi \
        -opensource \
        -confirm-license \
        -release \
        -shared \
        -xplatform android-clang \
        -nomake tests \
        -nomake examples \
        -no-spellchecker 


