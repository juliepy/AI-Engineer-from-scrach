#!/bin/bash

read -p "input yes or no:" input

case $input in
	yes|y|Y|YES)
		echo "you select yes"
		;;
	no|n|N|NO)
		echo "you select no"
		;;
	*)
		echo "invalid select"
		;;
esac
