#!/bin/bash
#

my_add() {
	echo "number of parameters: $#"
	echo "first parameter: $1"
	echo "2nd parameter: $2"
	return $(($1 + $2))
}

my_add 3 5
echo "retrun: $?"  # 8 get the return value of last cmd
