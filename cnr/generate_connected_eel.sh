#!/bin/bash

for (( i=1; i<=$1; i++))
do
    echo -n "0.0 nem:$i pathloss "
    for (( j=1; j<=$1; j++))
    do
        if [ $i -ne $j ]
        then
            echo -n "nem:$j,0.0 "
        fi
    done
    echo ""
done

