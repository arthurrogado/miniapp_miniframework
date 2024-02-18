from App.Utils.constants import ADMIN_ID
from urllib.parse import urlparse

def is_admin(userid):
    if userid == ADMIN_ID:
        return True
    
def dict_to_url_params(params: dict):
    # escape characters that are not allowed in url
    # example: {'name': 'John Doe?'} -> 'name=John%20Doe%3F'
    return "?" + '&'.join([f"{ urlparse(key) }={ urlparse(value) }" for key, value in params.items()])