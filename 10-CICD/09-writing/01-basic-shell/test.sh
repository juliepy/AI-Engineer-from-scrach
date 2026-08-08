#!/bin/bash
#
my_func(){
	local local_var="valid in func"
	global_var="whole script"
}

my_func
echo $local_var
echo $global_var

# echo "add.sh pid"
# ./add.sh
#

a=2
b=3

echo "call add script"
./add.sh $a $b
echo $1


echo "print string"
export mystr="hello"
echo $mystr

