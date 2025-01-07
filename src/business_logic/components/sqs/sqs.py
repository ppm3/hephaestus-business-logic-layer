"""Module to send messages to SQS queue"""
import os
import logging
import json
import datetime

from botocore.exceptions import ClientError

logLevel = os.getenv("LOG_LEVEL", "DEBUG")

logger = logging.getLogger(__name__)
logger.setLevel(logLevel)


def send_to_fifo(sqs, queue_url, body):
    """Send message to SQS FIFO queue"""
    try:
        logger.debug("Sending message to SQS: %s", json.dumps(body))
        unix_epoch_time = int(datetime.datetime.now().timestamp())
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                "phone_number": body.get("phone_number"),
                "message": body.get("message"),
            }),
            MessageGroupId=str(unix_epoch_time),
            MessageDeduplicationId=str(unix_epoch_time)
        )

        status_code = response.get(
            'ResponseMetadata', {}).get('HTTPStatusCode', 0)
        logger.debug(
            "[SQS] send_message response status code: %d", status_code)
        return status_code

    except ClientError as e:
        logger.error("Error sending message to SQS: %s",
                     json.dumps(e.response))
