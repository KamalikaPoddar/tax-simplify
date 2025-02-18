#!/usr/bin/env python3

from datetime import datetime, date
from decimal import Decimal
import json
import logging
import re
from http import HTTPStatus
import decimal
from decimal import Decimal
from typing import Optional, List, Dict, Any, Union, Tuple
import os
from io import BytesIO

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pydantic import BaseModel, validator, ValidationError

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for /api/ routes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rest of the existing code remains the same as in the original file

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
