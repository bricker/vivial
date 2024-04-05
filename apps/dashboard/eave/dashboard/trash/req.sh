#!/bin/bash
# flask run --debug

iters=10
i=0
while [[ $i -lt $iters ]]; do
	curl localhost:5000/test?vis_id=$RANDOM &
	i=$((i+1))
done

sleep 4