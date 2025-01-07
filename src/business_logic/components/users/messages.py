"""This module contains the functions to interact with the users table."""

import os
import json
import logging
import datetime

from business_logic.components.utils.utils import generate_nanoid

logLevel = os.getenv("LOG_LEVEL", "DEBUG")

logger = logging.getLogger(__name__)
logger.setLevel(logLevel)


def get_users_msg(users_messages_table, pk, sk):
    """Get the user message from the users_messages_table."""
    response = users_messages_table.get_item(
        Key={
            'pk': pk,
            'sk': sk
        }
    )

    logger.debug("[USER_MESSAGES] Getting user message: %s",
                 json.dumps(response))

    return response.get('Item', {})


def update_users_msg_status(users_messages_table,
                            user_message_row,
                            status='processed'):
    """Update the status to 'processed' in the users_messages_table."""
    user_message_row['status'] = status
    user_message_row['updated_at'] = datetime.datetime.now().isoformat()
    item = users_messages_table.put_item(Item=user_message_row)

    logger.debug(
        "[USER_MESSAGES] Status updated to 'processed': %s", json.dumps(item))
    return item.get('ResponseMetadata', {}).get('HTTPStatusCode', 0)


def register_message(users_messages_table, bot_id, message_data):
    """Register message in DynamoDB"""

    message_id = generate_nanoid()
    item = {
        'pk': message_id,
        'sk':  message_data['from'] + '#' + str(message_data['t']),
        'body': message_data['body'],
        'type': message_data['type'],
        'from': message_data['from'],
        'to': message_data['to'],
        'bot_id': bot_id,
        'deviceType': message_data.get('deviceType', 'Unknown'),
        'notifyName': message_data.get('notifyName', 'Unknown'),
        'status': 'raw',
        'created_at': datetime.datetime.now().isoformat(),
        'updated_at': datetime.datetime.now().isoformat()
    }
    users_messages_table.put_item(Item=item)
    logger.info("Message record: %s registered", message_id)
