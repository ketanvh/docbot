#!/bin/bash

if [ ! -f /home/site/wwwroot/app.py ]; then
  wget -O /tmp/app.zip https://github.com/ketanvh/docbot/archive/refs/heads/main.zip
  unzip /tmp/app.zip -d /tmp
  cp -r /tmp/docbot-main/* /home/site/wwwroot/
fi

gunicorn --bind=0.0.0.0 --timeout 600 app:app