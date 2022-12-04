#!/bin/bash

ROOT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
ANALIZATOR_DIR="${ROOT_DIR}/analizator"

for i in {1..13}
do
    rm "${ANALIZATOR_DIR}/reductions.txt" > /dev/null 2>&1
    rm "${ANALIZATOR_DIR}/LR_table.txt" > /dev/null 2>&1
    echo "#################################################################################################"
    echo "Test $i"
    python3 GSA.py < "$ROOT_DIR/testovi/test_$i/test.san"
    res=$(python3 $ANALIZATOR_DIR/SA.py < $ROOT_DIR/testovi/test_$i/test.in | diff $ROOT_DIR/testovi/test_$i/test.out -)
    if [ "$res" != "" ]
    then
        echo "FAIL"
        echo $res
    else
        echo "OK"
    fi
    rm "${ANALIZATOR_DIR}/reductions.txt" > /dev/null 2>&1
    rm "${ANALIZATOR_DIR}/LR_table.txt" > /dev/null 2>&1
done
