#!/bin/bash
#Ju Youn Chae
if [[ -z $1 || -z $2 ]]; then
	echo "Usage: <host> <port(s)>"
	return
fi

hosts=()
case $1 in *-*)
	IFS=- read start end <<< "$1"
	for ((host=start; host <= end; host++)); do
		hosts+=($host)
	done;; *,*)i
	IFS=, read -ra hosts <<< "$2";;*)
	hosts+=($1);;
esac
	
ports=()
case $2 in *-*)
	IFS=- read start end <<< "$2"
	for ((port=start; port <= end; port++)); do
		ports+=($port)
	done;; *,*)i 
	IFS=, read -ra ports <<< "$2";;*)
	ports+=($2);;
esac

for host in "${hosts[@]}"; do
	for port in "${ports[@]}"; do
		timeout ".1" bash -c "echo >/dev/tcp/$host/$port" &&
			echo "port $port is open" ||
			echo "port $port is closed"
	done
done
