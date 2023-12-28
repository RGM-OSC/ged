#!/bin/bash

if [ ! -n "$1" ]; then
	echo "You must specified a time in seconds for purge time."
	exit
else
	GapTime="$1"
fi

if [ ! -d /tmp/tmp-internal ]; then
	mkdir /tmp/tmp-internal
fi
CurrentStatus="`mktemp /tmp/tmp-internal/CurrentStatus_mk-XXXXX`"
CurrentGedActive="`mktemp /tmp/tmp-internal/CurrentGed-XXXXX`"

CurrentDate="`date +%s`"

echo "select id,equipment,service,state,contract,site,priority,criticity,warn_sla,crit_sla,extref_incident from ged.nagios_queue_active where l_sec < `expr $CurrentDate - $GapTime` ;" | mysql -u gedadmin --password='0rd0-c0m1735-b47h0n143' | tr '\t' ';' | sed -e 's: :@@:g' | grep -v "^id;" > ${CurrentGedActive}
awk 'BEGIN { printf("GET services\nColumns: host_name service_description state notifications_enabled\n");}' | /srv/rgm/mk-livestatus/bin/unixcat /srv/rgm/nagios/var/log/rw/live > ${CurrentStatus}

for i in `cat $CurrentGedActive`; do
	ID="`echo $i | cut -d';' -f1`"
	EQUIP="`echo $i | cut -d';' -f2`"
	SERV="`echo $i | cut -d';' -f3`"
	STATE="`echo $i | cut -d';' -f4`"
	CONTRACT="$(echo $i | cut -d ';' -f5)"
	SITE="$(echo $i | cut -d ';' -f6)"
	PRIORITY="$(echo $i | cut -d ';' -f7)"
	CRITICITY="$(echo $i | cut -d ';' -f8)"
	WARN_SLA="$(echo $i | cut -d ';' -f9)"
	CRIT_SLA="$(echo $i | cut -d ';' -f10)"
	EXTREF_INC="$(echo $i | cut -d ';' -f11)"
	EraseEquip="1"
	EraseService="1"
	Filter_Status="`cat $CurrentStatus | grep $EQUIP`"
	if [ ! -n "$Filter_Status" ]; then
		EraseEquip="0"
		echo "Filter Status empty."
		if [ ! -n "`echo $Filter_Status | grep $EQUIP`" ]; then
			EraseService="0"
			echo "Filter Status equip empty."
		fi
	fi
	if [ ! -n "`echo $Filter_Status | grep $SERV`" ]; then
		EraseService="0"
		echo "Filter Status Serv empty."
	fi

	if [[ $EraseEquip == 0 || $EraseService == 0 ]]; then
		/srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" ${STATE}
		echo "Droping event."
		continue
	fi

	for nagios_object in `cat $CurrentStatus | grep $EQUIP | grep $SERV`; do
		EQUIPN="`echo $nagios_object | cut -d';' -f1`"
		SERVN="`echo $nagios_object | cut -d';' -f2`"
		STATEN="`echo $nagios_object | cut -d';' -f3`"
    NOTIFENABLED="`echo $nagios_object | cut -d';' -f4`"
    if [ "$NOTIFENABLED" = "0" ]; then
      #Drop because of notification disabled
      echo "Notification disabled for $EQUIP/$SERV. Acknoledging event."
      /srv/rgm/ged/bin/gedq -push -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 0
      /srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 3
      /srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 2
      /srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 1
    else
		if [[ "$EQUIPN" = "$EQUIP" && "$SERVN" = "$SERV" ]]; then
			echo -n "The event $EQUIP of $SERV is in state $STATE."
			if [ ! "$STATEN" = "$STATE" ]; then
				echo " This is not a normal state. Let's update the event...."
				if [ "$STATEN" = "3" ]; then
				  # Push actual livestatus service state to UNKNOWN in active queue and delete all other status for same service
					/srv/rgm/ged/bin/gedq -push -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 3
					/srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 1
					/srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 2
					#Unknow in Nagios
				fi
				if [ "$STATEN" = "2" ]; then
				  # Push actual livestatus service state to CRITICAL in active queue and delete all other status for same service
          /srv/rgm/ged/bin/gedq -push -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 2
          /srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 1
          /srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 3
					#CRITICAL in Nagios
				fi
				if [ "$STATEN" = "1" ]; then
				  # Push actual livestatus service state to WARNING in active queue and delete all other status for same service
          /srv/rgm/ged/bin/gedq -push -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 1
          /srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 2
          /srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 3
					#WARNING in Nagios
				fi
				if [ "$STATEN" = "0" ]; then
					#OK in Nagios
          /srv/rgm/ged/bin/gedq -push -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 0
          /srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 0
          /srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 1
          /srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 2
          /srv/rgm/ged/bin/gedq -drop -type 1 "${CONTRACT}" "${SITE}" ${PRIORITY} ${CRITICITY} ${WARN_SLA} ${CRIT_SLA} "${EXTREF_INC}" "${EQUIP}" "`echo $SERV | sed -e 's:@@: :g'`" 3
				fi
			else
				echo " This is a normal state."
			fi
		fi
	fi
	done
done




rm -rf ${CurrentStatus}
rm -rf ${CurrentGedActive}
