#!/bin/bash

hosts=()
if [[ $1 == */* ]]; then
        hosts=$(prips $1)
fi

if [[ $1 == *-* ]]; then
        sta="$(cut -d '-' -f1 <<<"$1")"
        end="$(cut -d '-' -f2 <<<"$1")"
	sta2="$(cut -d '.' -f4 <<<"$sta")"
	end2="$(cut -d '.' -f4 <<<"$end")"
	base="$(cut -d '.' -f 1,2,3 <<<"$sta" --output-delimiter='.')"
	hosts=$(seq -f "$base.%g" $sta2 $end2)
fi

if [[ -z $hosts ]]; then
	hosts=$1
fi

for host in $hosts;  do
	echo "Testing $host"
	./portscan.sh $host $2
done
