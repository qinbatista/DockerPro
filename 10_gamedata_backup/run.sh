#!/bin/bash
service nginx reload
service nginx restart
python  gamedata_backup.py
