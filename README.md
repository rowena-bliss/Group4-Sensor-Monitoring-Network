# Group4-Sensor-Monitoring-Network
Group 4 project – Sensor Monitoring Network implemented using Python OOP.

#importing libraries 

from flask import Flask, render_template_string, jsonify

import sqlite#allows python to create and use an SQLite database.

import random

import time

import threading

app = Flask(__name__)

DATABASE = "sensor_data.db"
