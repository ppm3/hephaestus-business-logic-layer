"""Business logic for DynamoDB users."""
import os
import json
import logging

from botocore.exceptions import ClientError

logLevel = os.getenv("LOG_LEVEL", "DEBUG")

logger = logging.getLogger(__name__)
logger.setLevel(logLevel)


def register_or_update_user(atlas_users_table, data):
    """Register or update user in DynamoDB"""
    response = atlas_users_table.get_item(
        Key={'pk': data['pk'], 'sk': data['sk']})

    if 'Item' not in response:
        atlas_users_table.put_item(Item=data)

        logger.info("User %s registered", data['pk'])
    else:
        atlas_users_table.update_item(
            Key={'pk': data['pk'], 'sk': data['sk']},
            UpdateExpression="set updated_at = :updated_at",
            ExpressionAttributeValues={
                ':updated_at': data['updated_at']
            }
        )

        logger.info("User %s found, updating", data['pk'])


def find_user(atlas_users_table, user_id):
    """Find the user in the atlas_users_table using user_id."""
    try:
        response = atlas_users_table.get_item(
            Key={
                'pk': f"user|{user_id}",
                'sk': user_id
            }
        )
        return response.get('Item', {})
    except ClientError as e:
        logger.error("Error finding user in atlas_users_table: %s",
                     json.dumps(e.response))
        return {}
