#!/bin/bash
#

# grade funcion
check_grade(){
	local score=$1
	if [ $score -ge 90 ]; then
		echo "best"
	elif [ "$score" = "-1" ]; then
		echo "good"
	elif [ $score -ge 60 ]; then
		echo "ok"
	else
		echo "bad"
	fi
}


# 主逻辑
echo "==========student management ===="

while true; do
	read -p "input your score or exit with -1:	 " score

	#verify score
	if [ "$score" = "-1" ]; then
		echo "exit system"
		break
        fi

	#score
	if [ $score -lt 0 ] || [ $score -gt 100 ]; then
		echo "score must be in 0-100"
		continue
	fi

	grade=$(check_grade $score)
	echo "score grade: $grade"
done
