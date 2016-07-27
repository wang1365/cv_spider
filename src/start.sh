#!/bin/sh

echo "test"
pid=`cat "pid.txt"`

echo $pid
 kill -9 $pid

nohup python cv_fetch_main.py&

