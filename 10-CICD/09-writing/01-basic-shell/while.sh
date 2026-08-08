#!/bin/bash
#

i=1
while [ $i -le 3 ]; do
	read -p "请输入密码：" input
	if [ "$input" = "123" ]; then
		echo "密码正确"
		break
	fi
	let i+=1
done

if [ $i -gt 3 ]; then
	echo "次数超限， 退出"
	exit 1
fi

