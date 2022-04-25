#!/bin/bash
# このファイルはUTF-8で保存するべき

function service_status()
{
	if [ $DISTRIB_RELEASE = "18.04" ] ; then
		TMP=`systemctl list-units --all --type=service | grep $1`
		if [ -z "$TMP" ];then
			echo -n "\"service.$1\":\"none\" "
			return
		fi

		TMP=`systemctl status $1 | awk '/Active\:/ {print $2}'`
		if [ "$TMP" = "active" ]; then
			echo -n "\"service.$1\":\"run\" "
		else
			if [ "$TMP" = "inactive" ];then
				echo -n "\"service.$1\":\"stop\" "
			else
				echo -n "\"service.$1\":\"none\" "
			fi
		fi
	fi
	if [ $DISTRIB_RELEASE = "14.04" ] ; then
		TMP=`service $1 status 2>&1`
		if [[ "$TMP" == *start/running* ]];then
			echo -n "\"service.$1\":\"run\" "
		else
			if [[ "$TMP" == *stop/waiting* ]];then
				echo -n "\"service.$1\":\"stop\" "
			else
				echo -n "\"service.$1\":\"none\" "
			fi
		fi
	fi
}

function cszservice_status()
{
	TMP=`ps -e | grep $1`
	if [ -n "$TMP" ];then
		echo -n "\"service.$1\":\"run\" "
	else
		echo -n "\"service.$1\":\"stop\" "
	fi
}

echo "Content-type: text/plain"
echo ""
echo -n "{"

DATETIME=`date "+%Y/%m/%d %H:%M:%S"`
echo -n "\"datetime\":\"$DATETIME\" "
echo -n ","
if [[ "$DATETIME" == *1970/* ]]; then
  echo -n "\"date_not_set\":true "
else
  echo -n "\"date_not_set\":false "
fi

CPU_US=`vmstat | awk '/[0-9]/ {print $13}'`
CPU_SY=`vmstat | awk '/[0-9]/ {print $14}'`
CPU_ID=`vmstat | awk '/[0-9]/ {print $15}'`
CPU_WA=`vmstat | awk '/[0-9]/ {print $16}'`
echo -n ","
echo -n "\"cpu_us\":\"$CPU_US\" "
echo -n ","
echo -n "\"cpu_sy\":\"$CPU_SY\" "
echo -n ","
echo -n "\"cpu_id\":\"$CPU_ID\" "
echo -n ","
echo -n "\"cpu_wa\":\"$CPU_WA\" "

if [ "$1" = "timeonly" ]; then
	echo -n ","
	echo -n "\"timeonly\":true "

	echo "}"
	exit 0
fi

echo -n ","
echo -n "\"timeonly\":false "

#-----------------------------------------------------------------------
# system
#-----------------------------------------------------------------------

# kernelの表示
echo -n ","
echo -n "\"kernel\":\"`uname -r`\" "

# Distributionの表示
DISTRIB_ID=`awk -F= '/DISTRIB_ID=/ {print $2}' /etc/lsb-release`
DISTRIB_RELEASE=`awk -F= '/DISTRIB_RELEASE=/ {print $2}' /etc/lsb-release`
echo -n ","
echo -n "\"os\":\"$DISTRIB_ID $DISTRIB_RELEASE\" "

# CPU infoの表示
CPUINFO=`cat /proc/cpuinfo | awk -F ':' '(/model name/) || (/MIPS/) {print $2}' | sed -e "s/^ //" | sed -z "s/\n/ /g"`
echo -n ","
echo -n "\"cpuinfo\":\"$CPUINFO\" "

# Memory info
MEMTOTAL=`cat /proc/meminfo | awk -F ':' '(/MemTotal/) {print $2}' | sed -e "s/^ *//"`
MEMFREE=`cat /proc/meminfo | awk -F ':' '(/MemFree/) {print $2}' | sed -e "s/^ *//"`
MEMAVAILABLE=`cat /proc/meminfo | awk -F ':' '(/MemAvailable/) {print $2}' | sed -e "s/^ *//"`
MEMBUFF=`cat /proc/meminfo | awk -F ':' '(/Buffers/) {print $2}' | sed -e "s/^ *//"`
MEMCACHE=`cat /proc/meminfo | awk -F ':' '(/^Cached/) {print $2}' | sed -e "s/^ *//"`
echo -n ","
echo -n "\"memtotal\":\"$MEMTOTAL\" "
echo -n ","
echo -n "\"memfree\":\"$MEMFREE\" "
echo -n ","
echo -n "\"memavailable\":\"$MEMAVAILABLE\" "
echo -n ","
echo -n "\"membuffer\":\"$MEMBUFF\" "
echo -n ","
echo -n "\"memcache\":\"$MEMCACHE\" "

DISKINFO=`df --block-size=1048576 | awk '/\/dev\/root/ {print "Total:" $2 "MB<br> Used:" $3 "MB (" $5")<br> Free:" $4 "MB"}'`
echo -n ","
echo -n "\"diskinfo\":\"$DISKINFO\" "

#-----------------------------------------------------------------------
# network
#-----------------------------------------------------------------------

HOSTNAME=`hostname`
echo -n ","
echo -n "\"hostname\":\"$HOSTNAME\" "

echo "}"
