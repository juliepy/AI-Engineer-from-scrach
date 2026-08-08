#!/bin/bash
#

input="abc"

if [ "$input" = "abc" ]; then
	echo "相等"
fi

num=200
if [ $num -gt 100 ]; then
	echo "大于100"
else
	echo "小于等于100"
fi

file="./hello.sh"
if [ -d "$file" ]; then
	echo "$file 是目录"
elif [ -f "$file" ]; then
	echo "$file 是普通文件"
else
	echo "$file 不存在"
fi
