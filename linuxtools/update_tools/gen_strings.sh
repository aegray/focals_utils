#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


for file in $@
do
    echo "=================================="
    echo "${file}: "
    echo "=================================="
    python3 ${DIR}/read_bsdiff_extra_section.py ${file}

done

