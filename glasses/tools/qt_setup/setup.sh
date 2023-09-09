#!/bin/bash



DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"





cp $DIR/qprocessordetection.h qtbase/src/corelib/global/
cp $DIR/android-clang-pre/* qtbase/mkspecs/android-clang/
cp $DIR/android.prf qtbase/mkspecs/features/android/
cp $DIR/setup_crosscompile.sh .
./setup_crosscompile.sh



