import hashlib
id ='12345'
def hash_message(message):
    msg_bytes = message.encode('utf-8')
    sha1 = hashlib.sha1(msg_bytes)
    hex_digest = sha1.hexdigest()
    
    return hex_digest
    
def get_message(table):
    
    response = table.get_item(Key={'id': id})
    if 'Item' in response and 'message' in response['Item']:
        return response['Item']['message']
    return None

    
def set_message(table, message):
    
    table.update_item(
        Key={'id': id},
        UpdateExpression="SET message = :value",
        ExpressionAttributeValues={':value': hash_message(message)}
    )