#!/bin/bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Run ./run.py and check 127.0.0.1:5000 for seeing sociometry!"
