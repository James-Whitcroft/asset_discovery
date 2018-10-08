#!/bin/bash
#Ju Youn Chae
if [[ -z $1 || -z $2 ]]; then
	echo "Usage: <host> <port(s)>"
	return
fi
host=$1
ports=()
case $2 in *-*)
	IFS=- read start end <<< "$2"
	for ((port=start; port <= end; port++)); do
		ports+=($port)
	done;; *,*)i 
	IFS=, read -ra ports <<< "$2";;*)
	ports+=($2);;
esac

	for port in "${ports[@]}"; do
		timeout ".1" bash -c "echo >/dev/tcp/$host/$port" &&
			echo "port $port is open" ||
			echo "port $port is closed"
	done
