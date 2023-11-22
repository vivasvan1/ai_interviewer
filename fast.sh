#!/bin/bash

python -m venv venv
source venv/bin/activate

apt install build-essential

pip3 install -r requirements.txt

uvicorn main:app --reload --port 3000
