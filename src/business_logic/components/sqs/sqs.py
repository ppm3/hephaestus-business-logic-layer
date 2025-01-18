"""Module to send messages to SQS queue"""
import os
import logging
import json
import datetime
import hashlib

from botocore.exceptions import ClientError

logLevel = os.getenv("LOG_LEVEL", "DEBUG")

logger = logging.getLogger(__name__)
logger.setLevel(logLevel)


def send_to_fifo(sqs, queue_url, body, message_group_id, channel):
    """Send message to SQS FIFO queue"""
    logger.debug("Sending message to SQS: %s", json.dumps(body))

    message_group_id += '_' + str(channel)
    message_duplication_id = hashlib.md5(
        json.dumps(body).encode('utf-8')).hexdigest()

    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(body),
        MessageGroupId=message_group_id,
        MessageDeduplicationId=str(message_duplication_id)
    )

    status_code = response.get(
        'ResponseMetadata', {}).get('HTTPStatusCode', 0)
    logger.debug(
        "[SQS] send_message response status code: %d", status_code)
    return status_code


def send(sqs, queue_url, body):
    """Send message to SQS queue"""
    logger.debug("Sending message to SQS: %s", json.dumps(body))

    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(body)
    )

    status_code = response.get(
        'ResponseMetadata', {}).get('HTTPStatusCode', 0)
    logger.debug(
        "[SQS] send_message response status code: %d", status_code)
    return status_code
