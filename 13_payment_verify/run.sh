#!/bin/bash
service nginx reload
service nginx restart
python3 payment_verify.py
