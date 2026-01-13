# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

IOTHUB_NAME = os.getenv("IOTHUB_NAME")
IOTHUB_POLICY_NAME = os.getenv("IOTHUB_POLICY_NAME")
IOTHUB_POLICY_KEY = os.getenv("IOTHUB_POLICY_KEY")

if not all([IOTHUB_NAME, IOTHUB_POLICY_NAME, IOTHUB_POLICY_KEY]):
    raise RuntimeError("Missing IoT Hub config in .env")
