#!/bin/sh
export TZ=JST-9
echo "Content-Type: text/plain"
echo ""

if [ -e /etc/ntp.conf ]; then
	NTP_SERVER=`awk '/server/ {print $2}' /etc/ntp.conf | sed -z 's/\n/ /g'`
fi

RESULT=`ntpdate -v $NTP_SERVER 2>&1 | sed -z 's/\n/<br>/g'`
echo $RESULT
