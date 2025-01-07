"""This module contains the functions to interact with the flow DynamoDB table."""


def get_flow_item(atlas_flow_table, bot_id, sk):
    """Get the flow item from the DynamoDB table using bot_id and sk."""
    response = atlas_flow_table.get_item(
        Key={
            'pk': bot_id,
            'sk': sk.replace("state|", "")
        }
    )

    return response.get('Item', {})
