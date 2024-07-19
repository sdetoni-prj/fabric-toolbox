# Import necessary libraries
from msal import PublicClientApplication
from msal import ConfidentialClientApplication
import argparse
import json
import requests

# Define a function to acquire token using Entra SPN
def acquire_token_by_spn(tenant_id, client_id, client_secret):
        # Placeholder for access token
        access_token = "CALLING ACQUIRE TOKEN SPN FUNCTION"

        # Initialize the MSAL confidential client
        # Set up your configuration        
        config = {
            "client_id": client_id,
            "client_secret": client_secret,
            "authority": f"https://login.microsoftonline.com/{tenant_id}",
            "scope": ["https://api.fabric.microsoft.com/.default"]
        }

        # Create a ConfidentialClientApplication instance
        app = ConfidentialClientApplication(
              client_id=config["client_id"],
              client_credential=config["client_secret"],
              authority=config["authority"]
        )
             
        # Acquire token for client
        result = app.acquire_token_for_client(scopes=config["scope"])
        
        # Check if access token is in the result
        if 'access_token' in result:
            access_token = result['access_token']
        else:
           access_token = None

        return result

# Define a function to acquire token using AAD username password
def acquire_token_user_id_password(tenant_id, client_id,user_name,password):
    
    # Placeholder for access token
    access_token = "CALLING ACQUIRE TOKEN PASSWORD FUNCTION"
    authority = f'https://login.microsoftonline.com/{tenant_id}'
    
    # Create a PublicClientApplication instance
    app = PublicClientApplication(client_id, authority=authority)
    
    scopes = ['https://api.fabric.microsoft.com/.default']
    
    # Acquire token by username and password
    result = app.acquire_token_by_username_password(user_name, password, scopes)
    
    # Check if access token is in the result
    if 'access_token' in result:
        access_token = result['access_token']
    else:
      access_token = None
    
    return access_token

# Define a function to create a fabric workspace
def create_workspace(workspace_name, headers):

    # URL for creating workspace
    createworkspaceurl = 'https://api.fabric.microsoft.com/v1/workspaces'
    workspaceId = None
    
    print("Inside Create Workspace")
    
    # Payload for creating workspace
    payloadcreateworkspace = {
        "displayName": workspace_name
    }
    
    # Make the POST request
    response = requests.post(createworkspaceurl, headers=headers, json=payloadcreateworkspace)
    print(response.json())
    print(response.status_code)
    
    # Check if the workspace created successfully
    if response.status_code == 201:
        workspaceId =  response.json()['id']
        print(f'Workspace created successfully. Workspace ID: {workspaceId}')
  
    return workspaceId

# Define a function to assign capacity to workspace
def assing_capacity_to_workspace(workspace_id, headers, capacity_id):

        print("Inside Assign Capacity to Workspace")

        # URL for assigning capacity
        assingcapacityurl = f'https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/assignToCapacity'        
        payloadassigncapacity = {
            'capacityId': capacity_id
        }
        
        # Make the POST request
        response = requests.post(assingcapacityurl, headers=headers, json=payloadassigncapacity)
        
        # Check if the request was successful
        if response.status_code == 202:
            print('Request accepted, Capacity assignment is in progress.')
        else:
            print(f'Failed to assign capacity. Status Code: {response.status_code}')
        
        return None

# Define a function to assign workspace role
def assign_workspace_role(workspace_id, headers,tenant_userId,developer_UserId):

    print("Inside Assign Workspace Role")   
    
    # URL for assigning workspace role
    assignworkspaceroleurl = f'https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/roleAssignments'
    
    # List of user IDs
    workspace_userIds = [tenant_userId,developer_UserId]

    # Loop through each user ID
    for id in workspace_userIds:
            # Payload for assigning workspace role
            payloadassignworkspacerole = {
                 "principal": {
                      "Id": id,
                      "type": "User"
                 },
                 "role": "Admin"
            }
            
            # Make the POST request
            response = requests.post(assignworkspaceroleurl, headers=headers, json=payloadassignworkspacerole)
            
            # Check if the request was successful
            if response.status_code == 201:
                print('Request accepted, Workspace role assignment is in progress for user: ' + id)
            else:
                get_status = response.json()
                print(get_status)
                print(f'Failed to assign workspace role. Status Code: {response.status_code}')
    return None

# Main function
def main_func():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser()
    
    # Add arguments to the parser
    parser.add_argument('--tenant_id',type=str, help= 'TenantID passed from Devops')
    parser.add_argument('--client_id',type=str, help= 'ClientID passed from Devops')
    parser.add_argument('--client_secret',type=str, help= 'Secret passed from Devops')
    parser.add_argument('--user_name',type=str, help= 'User Name passed from Devops')
    parser.add_argument('--user_password',type=str, help= 'User password passed from Devops')
    parser.add_argument('--developerWorkspaceName',type=str, help= 'Name of the developer workspace to be created')
    parser.add_argument('--developerUserId',type=str, help= 'Developer email address to be assigned to worspace')
    parser.add_argument('--adminUserId',type=str, help= 'Tenant Admin Address')
    parser.add_argument('--capacityId',type=str, help= 'Developer Capacity ID to be used')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Define your tenant_id, client_id, client_secret, workspace_name, developer_username, project_name, repository_name, and branch_name
    tenant_id = args.tenant_id
    client_id = args.client_id
    client_secret = args.client_secret
    user_name = args.user_name
    user_password = args.user_password
    developerWorkspaceName = args.developerWorkspaceName    
    adminUserId = args.adminUserId
    capacityId = args.capacityId
    developerUserId = args.developerUserId

    # Acquire token
    access_token = None

    # Acquire token by username and password
    access_token = acquire_token_user_id_password(tenant_id, client_id,user_name,user_password)    
    #access_token = acquire_token_by_spn(tenant_id, client_id, client_secret)
    print (access_token)

    #set_devops_variable('ACCESS_TOKEN', access_token) # To set a ADO variable with the access token

    # Create the headers dictionary
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    #Create a fabric workspace
    workspace_id = create_workspace(developerWorkspaceName, headers)
    if workspace_id is not None:
        # Assign workspace role
        assign_workspace_role(workspace_id, headers,adminUserId,developerUserId)
        # Assign capacity to workspace
        assing_capacity_to_workspace(workspace_id, headers, capacityId)

# Call the main function
if __name__ == "__main__":
    main_func()