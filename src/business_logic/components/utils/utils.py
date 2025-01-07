"""Utility functions for the business logic layer."""
import os
import logging
import random
import json

logLevel = os.getenv("LOG_LEVEL", "DEBUG")
logger = logging.getLogger(__name__)
logger.setLevel(logLevel)


def clean_dynamodb_json(dynamodb_json):
    """Clean the DynamoDB JSON to make it more readable."""
    clean_json = {}
    for key, value in dynamodb_json.items():
        clean_json[key] = list(value.values())[0]
    return clean_json


def extract_record(event):
    """Extract the record from DynamoDB stream event."""
    if 'Records' in event and len(event['Records']) > 0:
        return event['Records'][0]
    return None


def generate_nanoid(size=21):
    """Generate a random nanoid-like string"""
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choices(alphabet, k=size))


def get_body(event):
    """Extracts the body from the event"""
    try:
        body = json.loads(event["body"])
    except (KeyError, json.JSONDecodeError) as e:
        logger.error("Error parsing body: %s", e)
        body = {}
    return body
