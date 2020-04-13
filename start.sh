#!/bin/bash
PKG_MANAGER=$( command -v yum || command -v apt-get )
sudo $PKG_MANAGER -y install epel-release
sudo $PKG_MANAGER -y install jpegoptim
sudo -H pip3 install -r requirements.txt
python3 manage.py makemigrations images
python3 manage.py migrate
python3 manage.py createcachetable
python3 manage.py runserver