import json
from azure.common.credentials import ServicePrincipalCredentials

with open('auth.json') as f:
  data = json.load(f)

# Tenant ID for your Azure Subscription
TENANT_ID = data["tenant"]

# Your Service Principal App ID
CLIENT = data["appId"]

# Your Service Principal Password
KEY = data["password"]

def Get_credentials():
  credentials = ServicePrincipalCredentials(client_id = CLIENT, secret = KEY, tenant = TENANT_ID)
  return credentials

