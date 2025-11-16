"""
Deploy Outlander Copilot Prompt Flow to Azure as a Managed Online Endpoint
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Model,
    Environment,
    CodeConfiguration,
)
from azure.identity import DefaultAzureCredential

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")


def deploy_flow():
    """Deploy the Outlander Copilot flow to Azure."""
    
    print("=" * 80)
    print("DEPLOYING OUTLANDER COPILOT TO AZURE")
    print("=" * 80)
    
    # Get Azure credentials
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    workspace_name = os.getenv("AZURE_AI_HUB_NAME", "outlander-hub")
    
    print(f"\nSubscription: {subscription_id}")
    print(f"Resource Group: {resource_group}")
    print(f"Workspace: {workspace_name}")
    
    # Authenticate
    print("\n[1/5] Authenticating with Azure...")
    try:
        credential = DefaultAzureCredential()
        ml_client = MLClient(
            credential=credential,
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name=workspace_name
        )
        print("✓ Authentication successful")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return False
    
    # Create endpoint
    endpoint_name = "outlander-copilot-endpoint"
    print(f"\n[2/5] Creating managed online endpoint: {endpoint_name}...")
    
    try:
        endpoint = ManagedOnlineEndpoint(
            name=endpoint_name,
            description="Outlander Gear Co. AI Copilot - RAG-based product assistant",
            auth_mode="key",
            tags={
                "project": "outlander-copilot",
                "type": "rag-chatbot",
                "framework": "promptflow"
            }
        )
        
        # Check if endpoint exists
        try:
            existing_endpoint = ml_client.online_endpoints.get(endpoint_name)
            print(f"✓ Endpoint already exists: {existing_endpoint.scoring_uri}")
        except:
            # Create new endpoint
            endpoint_result = ml_client.online_endpoints.begin_create_or_update(endpoint).result()
            print(f"✓ Endpoint created: {endpoint_result.scoring_uri}")
    except Exception as e:
        print(f"✗ Endpoint creation failed: {e}")
        return False
    
    # Register the flow as a model
    print("\n[3/5] Registering Prompt Flow as model...")
    flow_path = project_root / "prompt_flows" / "outlander_copilot"
    
    try:
        model = Model(
            name="outlander-copilot-model",
            path=str(flow_path),
            type="custom_model",
            description="Outlander Copilot RAG flow with Azure AI Search and GPT-4o"
        )
        
        registered_model = ml_client.models.create_or_update(model)
        print(f"✓ Model registered: {registered_model.name} (version {registered_model.version})")
    except Exception as e:
        print(f"✗ Model registration failed: {e}")
        return False
    
    # Create deployment
    deployment_name = "outlander-copilot-deployment-v1"
    print(f"\n[4/5] Creating deployment: {deployment_name}...")
    
    try:
        deployment = ManagedOnlineDeployment(
            name=deployment_name,
            endpoint_name=endpoint_name,
            model=registered_model.id,
            instance_type="Standard_DS3_v2",  # 4 cores, 14GB RAM
            instance_count=1,
            environment_variables={
                "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
                "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
                "AZURE_DEPLOYMENT_NAME": os.getenv("AZURE_DEPLOYMENT_NAME"),
                "AZURE_SEARCH_ENDPOINT": os.getenv("AZURE_SEARCH_ENDPOINT"),
                "AZURE_SEARCH_INDEX_NAME": os.getenv("AZURE_SEARCH_INDEX_NAME"),
            }
        )
        
        deployment_result = ml_client.online_deployments.begin_create_or_update(deployment).result()
        print(f"✓ Deployment created successfully")
        
        # Set traffic to 100% for this deployment
        endpoint.traffic = {deployment_name: 100}
        ml_client.online_endpoints.begin_create_or_update(endpoint).result()
        print(f"✓ Traffic set to 100% for {deployment_name}")
        
    except Exception as e:
        print(f"✗ Deployment failed: {e}")
        return False
    
    # Get endpoint details
    print("\n[5/5] Retrieving deployment details...")
    try:
        endpoint = ml_client.online_endpoints.get(endpoint_name)
        keys = ml_client.online_endpoints.get_keys(endpoint_name)
        
        print("\n" + "=" * 80)
        print("DEPLOYMENT SUCCESSFUL!")
        print("=" * 80)
        print(f"\nEndpoint Name: {endpoint.name}")
        print(f"Scoring URI: {endpoint.scoring_uri}")
        print(f"Primary Key: {keys.primary_key[:20]}...")
        print(f"Status: {endpoint.provisioning_state}")
        
        # Save deployment info
        deployment_info = {
            "endpoint_name": endpoint.name,
            "scoring_uri": endpoint.scoring_uri,
            "deployment_name": deployment_name,
            "primary_key": keys.primary_key,
            "status": endpoint.provisioning_state,
            "deployed_at": str(endpoint.created_at) if hasattr(endpoint, 'created_at') else None
        }
        
        output_file = project_root / "deployment_info.json"
        with open(output_file, 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print(f"\n✓ Deployment info saved to: {output_file}")
        
        # Print test command
        print("\n" + "=" * 80)
        print("TEST YOUR DEPLOYMENT")
        print("=" * 80)
        print("\nUsing Python:")
        print(f'''
import requests
import json

url = "{endpoint.scoring_uri}"
headers = {{
    "Content-Type": "application/json",
    "Authorization": f"Bearer {keys.primary_key}"
}}

data = {{
    "chat_input": "Which tent is the most waterproof?",
    "chat_history": []
}}

response = requests.post(url, headers=headers, json=data)
print(response.json())
''')
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to retrieve endpoint details: {e}")
        return False


if __name__ == "__main__":
    success = deploy_flow()
    exit(0 if success else 1)
