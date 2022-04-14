#!/bin/bash
service nginx reload
service nginx restart
python config_request.py
