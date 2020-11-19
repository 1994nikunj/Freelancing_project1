#!/bin/bash

NODES="host_name"
for i in $NODES
do
   # ssh "$i" "pwd && ps -aux && exit"
   echo "$i"
done
