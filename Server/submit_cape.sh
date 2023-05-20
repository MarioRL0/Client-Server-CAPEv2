#!/bin/bash

cd /opt/CAPEv2

sudo -u cape poetry run python utils/submit.py -d --platform windows  --route "internet" --machine win10 "$1"
