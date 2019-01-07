#!/bin/bash

## Copyright Carl Bingel 2019

##
##  Pushes meter readings to MQTT server
##

READER_SCRIPT="./modbusMeterReader.py"

if ! which mosquitto_pub > /dev/null
then
  echo "ERROR: This script requires the mosquitto_pub command to be present (on debian based systems, install with 'sudo apt-get install mosquitto-clients')"
  exit 4
fi

## Default options
MQTT_HOSTNAME="localhost"
MQTT_PORT="1883"
MQTT_USERNAME=""
MQTT_PASSWORD=""
MQTT_TOPIC="modbusMeterReader/meter1"
VERBOSE=false

## Parse command line options, removing the ones recognised by this script, keeping
## the rest for sending to modbusMeterReader.py
## A little kludgy - but works...
ARGS=( $* )
ARG_PTR=0
while (( $ARG_PTR < ${#ARGS[@]} )) ; do
  OPT="${ARGS[$ARG_PTR]}"
  #echo "ARG_PTR=$ARG_PTR, #=${#ARGS[@]}, OPT='$OPT', Arglist: ${ARGS[*]}"
  case "$OPT" in
    --mqtt-hostname)
      #unset ARGS[ARG_PTR]
      ARGS=( ${ARGS[@]:0:$ARG_PTR} ${ARGS[@]:$ARG_PTR+1} )
      MQTT_HOSTNAME="${ARGS[$ARG_PTR]}"
      ARGS=( ${ARGS[@]:0:$ARG_PTR} ${ARGS[@]:$ARG_PTR+1} )
      ;;
    --mqtt-port)
      ARGS=( ${ARGS[@]:0:$ARG_PTR} ${ARGS[@]:$ARG_PTR+1} )
      MQTT_PORT="${ARGS[$ARG_PTR]}"
      ARGS=( ${ARGS[@]:0:$ARG_PTR} ${ARGS[@]:$ARG_PTR+1} )
      ;;
    --mqtt-username)
      ARGS=( ${ARGS[@]:0:$ARG_PTR} ${ARGS[@]:$ARG_PTR+1} )
      MQTT_USERNAME="${ARGS[$ARG_PTR]}"
      ARGS=( ${ARGS[@]:0:$ARG_PTR} ${ARGS[@]:$ARG_PTR+1} )
      ;;
    --mqtt-password)
      ARGS=( ${ARGS[@]:0:$ARG_PTR} ${ARGS[@]:$ARG_PTR+1} )
      MQTT_PASSWORD="${ARGS[$ARG_PTR]}"
      ARGS=( ${ARGS[@]:0:$ARG_PTR} ${ARGS[@]:$ARG_PTR+1} )
      ;;
    --mqtt-topic)
      ARGS=( ${ARGS[@]:0:$ARG_PTR} ${ARGS[@]:$ARG_PTR+1} )
      MQTT_TOPIC="${ARGS[$ARG_PTR]}"
      ARGS=( ${ARGS[@]:0:$ARG_PTR} ${ARGS[@]:$ARG_PTR+1} )
      ;;
    --help | -h)
      echo "modbusMeterReaderMQTT.sh  Pushes meter readings to MQTT server"
      echo
      echo "usage:  modbusMeterReaderMQTT.sh <mqtt-options> <modbusMeterReader.py-options>"
      echo "  --mqtt-hostname <hostname>    Hostname of MQTT server (default=localhost)"
      echo "  --mqtt-port <port>            Port for MQTT server (default=1883)"
      echo "  --mqtt-username <username>    Username for MQTT server"
      echo "  --mqtt-password <password>    Password for MQTT server"
      echo "  --mqtt-topic <topic>          Topic for MQTT publish (default=modbusMeterReader/meter1)"
      echo
      echo "*** BELOW ARE COMMAND LINE OPTIONS FOR THE MODBUS SCRIPT ***"
      echo
      $READER_SCRIPT -h
      exit 3
      ;;
    -v)
      VERBOSE=true
      ARG_PTR=$[$ARG_PTR + 1]
      ;;
    *)
      ARG_PTR=$[$ARG_PTR + 1]
      ;;
  esac
done

if $VERBOSE
then
  echo "MQTT_HOSTNAME: $MQTT_HOSTNAME"
  echo "MQTT_PORT: $MQTT_PORT"
  echo "MQTT_TOPIC: $MQTT_TOPIC"
  echo "MQTT_USERNAME: $MQTT_USERNAME"
  echo "MQTT_PASSWORD: $MQTT_PASSWORD"
  echo "REMAINING CMDLINE: ${ARGS[@]}"
fi

## Do reading
READING="$($READER_SCRIPT ${ARGS[@]})"
READER_EXITLEVEL=$?

if [[ $READER_EXITLEVEL != 0 ]]; then
  echo "!!! modbusMeterReader.py failed"
  exit 1
fi

if $VERBOSE
then
  echo "*** METER READING START ***"
  echo $READING | jq .
  echo "*** METER READING END ***"
fi


if [ "$MQTT_USERNAME" = "" ]; then
  echo $READING | mosquitto_pub -s -h $MQTT_HOSTNAME -p $MQTT_PORT -t $MQTT_TOPIC
  MQTTPUB_EXITLEVEL=$?
else
  echo $READING | mosquitto_pub -s -h $MQTT_HOSTNAME -p $MQTT_PORT -t $MQTT_TOPIC -u $MQTT_USERNAME -P "$MQTT_PASSWORD"
  MQTTPUB_EXITLEVEL=$?
fi

if [[ $MQTTPUB_EXITLEVEL != 0 ]]; then
  echo "!!! mosquitto_pub failed"
  exit 2
fi

echo "*** Success!"
exit 0
