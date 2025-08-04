#!/bin/sh

echo $@
echo $1
echo $2
echo $#

export TC_TOKEN='eyJ0eXAiOiAiVENWMiJ9.dW0tb3E0bnRrZjNpWlhZZkIwVW5Hb2RlYy1V.NmFmNTljN2QtMGRmZC00YzA4LTkzOWMtOWJmMjZkZGE2YmYy'

# Get the argument
ARG="$1"

# Use case statement for better scalability
case "$ARG" in
    "CA42")
        echo "Running stage for CA42..."
		export DEVICE_IP='192.168.5.51'
		export USERNAME='root'
		export PASSWORD='getac123'
		export RTSP_USERNAME='admin'
		export RTSP_PASSWORD='4200'
		export PROJECT_ROOT='/home/jenkins/ca42-automation'
        ;;
    "CA42-A")
        echo "Running stage for CA42-A..."
		export DEVICE_IP='192.168.5.52'
		export USERNAME='root'
		export PASSWORD='getac123'
		export RTSP_USERNAME='admin'
		export RTSP_PASSWORD='4200'
		export PROJECT_ROOT='/home/jenkins/ca42a-automation'
        ;;
	"CA22-G2")
	    echo "Running stage for CA22-G2..."
		export DEVICE_IP='192.168.5.X'
		export USERNAME='root'
		export PASSWORD='getac123'
		export RTSP_USERNAME='admin'
		export RTSP_PASSWORD='2100'
		export PROJECT_ROOT='/home/jenkins/ca22-g2-automation'
	    ;;
    *)
        echo "Error: Invalid argument."
        echo "Please specify a correct argument: CA42 or CA42-A or CA22-G2"
        exit 1
        ;;
esac

# Verify they are set:
echo "DEVICE_IP=$DEVICE_IP"
echo "USERNAME=$USERNAME"
echo "PASSWORD=$PASSWORD"
echo "RTSP_USERNAME=$RTSP_USERNAME"
echo "RTSP_PASSWORD=$RTSP_PASSWORD"
echo "TC_TOKEN=$TC_TOKEN"
echo "PROJECT_ROOT=$PROJECT_ROOT"
