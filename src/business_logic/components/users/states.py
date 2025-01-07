"""This module contains the functions to interact with the user_states DynamoDB table."""
import os
import json
import logging
import datetime

import boto3

logLevel = os.getenv("LOG_LEVEL", "DEBUG")

logger = logging.getLogger(__name__)
logger.setLevel(logLevel)


def get_user_state(user_states_table, bot_id, user_id):
    """Get the user state from the DynamoDB table sorted by update date."""
    response = user_states_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('pk').eq(bot_id + "|user") &
        boto3.dynamodb.conditions.Key('sk').begins_with('state|' + user_id),
        ScanIndexForward=False,
        Limit=1
    )
    items = response.get('Items', [])
    return items[0] if items else {}


def update_status_to_processed(user_states_table, user_state_row, status='processed'):
    """Update the status to 'processed' in the user_states_table."""
    user_state_row['status'] = status
    user_state_row['updated_at'] = datetime.datetime.now().isoformat()
    item = user_states_table.put_item(Item=user_state_row)

    logger.debug(
        "[USER_STATES] Status updated to 'processed': %s", json.dumps(item))
    return item.get('ResponseMetadata', {}).get('HTTPStatusCode', 0)


def insert_next_state(user_states_table, pk, next_node):
    """Insert the next state into the user_states_table."""
    item = {
        "pk": pk,
        "sk": "state|node|" + next_node['node_ref'],
        "messages_rows": [],
        "message_row_identifier": '',
        "original_message": '',
        "status": "raw",
        'created_at': datetime.datetime.now().isoformat(),
        'updated_at': datetime.datetime.now().isoformat()
    }

    logger.debug("TO inserting next state: %s", json.dumps(item))

    user_states_table.put_item(Item=item)
    logger.debug("Next state inserted: %s", json.dumps(item))


def save_user_state(user_states_table, bot_id, flow_id, message_row, status='raw'):
    """Save or update the user state in the DynamoDB table."""
    user_id = message_row.get('from')
    pk = bot_id + '|' + user_id
    sk = 'state|' + flow_id

    # Check if the item already exists
    response = user_states_table.get_item(Key={'pk': pk, 'sk': sk})
    item = response.get('Item', {})

    db_action = 'updated' if item else 'created'

    if item:
        # If the item exists and the status is not 'completed', update it
        if item.get('status') != 'completed':
            item['message_row_identifiers'].append(
                message_row.get('pk') + '|' + message_row.get('sk'))
            item['updated_at'] = datetime.datetime.now().isoformat()

            logger.debug("Updating item with values: %s", item)
        else:
            logger.debug("Record is completed, not updating the message rows.")
    else:
        # If the item does not exist, create a new one
        item = {
            'pk': pk,
            'sk': sk,
            'status': status,
            'message_row_identifier': message_row.get('pk') + '|' + message_row.get('sk'),
            'message_row_identifiers': [message_row.get('pk') + '|' + message_row.get('sk')],
            'created_at': datetime.datetime.now().isoformat(),
            'updated_at': datetime.datetime.now().isoformat()
        }

    if db_action == 'created':
        response = user_states_table.put_item(Item=item)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logger.debug("Successfully saved user state for user: %s", user_id)
            return True
    else:
        response = user_states_table.update_item(
            Key={'pk': pk, 'sk': sk},
            UpdateExpression="set messages_rows = :messages_rows, updated_at = :updated_at",
            ExpressionAttributeValues={
                ':messages_rows': item['messages_rows'],
                ':updated_at': item['updated_at']
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logger.debug(
                "Successfully updated user state for user: %s", user_id)
            return True

    logger.error("Failed to save user state for user: %s", user_id)
    return False


def get_last_raw_record(user_states_table, bot_id, user_id, status='raw'):
    """Get the last record of user_id with raw status from the DynamoDB table."""
    response = user_states_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('pk').eq(bot_id + "|user") &
        boto3.dynamodb.conditions.Key('sk').begins_with('state|' + user_id),
        FilterExpression=boto3.dynamodb.conditions.Attr('status').eq(status),
        ScanIndexForward=False,
        Limit=1
    )
    items = response.get('Items', [])
    return items[0] if items else {}
