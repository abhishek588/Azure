import ConnectAzure_authentication as ca
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource.resources import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption
import os
import json

#Get azure subscription Id
azure_subscription_command = os.popen('az account list').read()
azure_subscription_list = json.loads(azure_subscription_command)
azure_subscription = azure_subscription_list[0]
azure_subscription_id = azure_subscription["id"]

#input from user
LOCATION = input("Enter Location: ")
GROUP_NAME = input("Enter Resource Group Name: ")
VM_NAME = input("Enter VM Name: ")

#create connection
compute_client = ComputeManagementClient(ca.Get_credentials(), azure_subscription_id)
resource_client = ResourceManagementClient(ca.Get_credentials(), azure_subscription_id)
network_client = NetworkManagementClient(ca.Get_credentials(), azure_subscription_id)

resource_group_list = []
count = 0
for rg in resource_client.resource_groups.list():
    resource_group_list.append(rg.name)

for name in resource_group_list:
    if GROUP_NAME == name:
        count = count + 1
        print("\nResource group name exists. Please provide a different name.\n")
        break

def create_resource_group(resource_client):
    resource_group_params = { 'location':LOCATION }
    print("\nCreating resource group...\n ")
    resource_group_result = resource_client.resource_groups.create_or_update(
        GROUP_NAME, 
        resource_group_params
    )

def create_public_ip_address(network_client):
    public_ip_addess_params = {
        'location': LOCATION,
        'public_ip_allocation_method': 'Dynamic'
    }
    creation_result = network_client.public_ip_addresses.create_or_update(
        GROUP_NAME,
        'myIPAddress',
        public_ip_addess_params
    )
    return creation_result.result()

def create_vnet(network_client):
    vnet_params = {
        'location': LOCATION,
        'address_space': {
            'address_prefixes': ['10.0.0.0/16']
        }
    }
    creation_result = network_client.virtual_networks.create_or_update(
        GROUP_NAME,
        'myVNet',
        vnet_params
    )
    return creation_result.result()

def create_subnet(network_client):
    subnet_params = {
        'address_prefix': '10.0.0.0/24'
    }
    creation_result = network_client.subnets.create_or_update(
        GROUP_NAME,
        'myVNet',
        'mySubnet',
        subnet_params
    )

    return creation_result.result()

def create_nic(network_client):
    subnet_info = network_client.subnets.get(
        GROUP_NAME, 
        'myVNet', 
        'mySubnet'
    )
    publicIPAddress = network_client.public_ip_addresses.get(
        GROUP_NAME,
        'myIPAddress'
    )
    nic_params = {
        'location': LOCATION,
        'ip_configurations': [{
            'name': 'myIPConfig',
            'public_ip_address': publicIPAddress,
            'subnet': {
                'id': subnet_info.id
            }
        }]
    }
    creation_result = network_client.network_interfaces.create_or_update(
        GROUP_NAME,
        'myNic',
        nic_params
    )

    return creation_result.result()

def create_vm(network_client, compute_client):  
    nic = network_client.network_interfaces.get(
        GROUP_NAME, 
        'myNic'
    )
    vm_parameters = {
        'location': LOCATION,
        'os_profile': {
            'computer_name': VM_NAME,
            'admin_username': 'azureuser',
            'admin_password': 'PythonLearn1234'
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1_v2'
        },
        'storage_profile': {
            'image_reference': {
                'publisher': 'MicrosoftWindowsServer',
                'offer': 'WindowsServer',
                'sku': '2016-Datacenter',
                'version': 'latest'
            }
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic.id
            }]
        }
    }
    creation_result = compute_client.virtual_machines.create_or_update(
        GROUP_NAME, 
        VM_NAME, 
        vm_parameters
    )
    return creation_result.result()

if count != 1:
    create_resource_group(resource_client)
    creation_result = create_public_ip_address(network_client)
    creation_result = create_vnet(network_client)
    creation_result = create_subnet(network_client)
    creation_result = create_nic(network_client)
    creation_result = create_vm(network_client, compute_client)
