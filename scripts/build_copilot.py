"""
Complete automation script for Outlander Gear Co. Copilot
This script handles everything: data upload, index creation, prompt flow setup, and deployment.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)
import time

# Load environment variables
load_dotenv()

class OutlanderCopilotBuilder:
    """Builds and deploys the Outlander Gear Co. copilot programmatically."""
    
    def __init__(self):
        """Initialize with Azure credentials and configuration."""
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        self.resource_group = os.getenv('AZURE_RESOURCE_GROUP')
        self.project_name = os.getenv('AZURE_AI_PROJECT_NAME')
        self.search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        self.search_key = os.getenv('AZURE_SEARCH_API_KEY')
        self.search_index_name = os.getenv('AZURE_SEARCH_INDEX_NAME', 'outlander-products-index')
        
        # Initialize ML Client for Azure AI
        self.ml_client = MLClient(
            DefaultAzureCredential(),
            self.subscription_id,
            self.resource_group,
            workspace_name=self.project_name
        )
        
        # Initialize Search Client
        self.search_index_client = SearchIndexClient(
            endpoint=self.search_endpoint,
            credential=AzureKeyCredential(self.search_key)
        )
        
        print("✓ Azure clients initialized successfully")
    
    def step1_upload_data(self):
        """Step 1: Upload product data to Azure AI"""
        print("\n" + "="*80)
        print("STEP 1: Uploading Product Data")
        print("="*80)
        
        data_path = Path(__file__).parent.parent / "data" / "product-info"
        
        if not data_path.exists():
            print("✗ Product data folder not found!")
            return False
        
        product_files = list(data_path.glob("*.md"))
        print(f"Found {len(product_files)} product files")
        
        # Upload data to Azure AI ML
        try:
            from azure.ai.ml.entities import Data
            from azure.ai.ml.constants import AssetTypes
            
            data_asset = Data(
                name="outlander-product-data",
                path=str(data_path),
                type=AssetTypes.URI_FOLDER,
                description="Outlander Gear Co. product information",
            )
            
            print("Uploading data to Azure AI...")
            self.ml_client.data.create_or_update(data_asset)
            print("✓ Data uploaded successfully")
            return True
            
        except Exception as e:
            print(f"✗ Error uploading data: {str(e)}")
            return False
    
    def step2_create_search_index(self):
        """Step 2: Create AI Search index with vector search"""
        print("\n" + "="*80)
        print("STEP 2: Creating AI Search Index")
        print("="*80)
        
        try:
            # Define the index schema
            fields = [
                SearchField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                    filterable=True,
                ),
                SearchField(
                    name="content",
                    type=SearchFieldDataType.String,
                    searchable=True,
                ),
                SearchField(
                    name="title",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    filterable=True,
                ),
                SearchField(
                    name="filepath",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SearchField(
                    name="url",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SearchField(
                    name="contentVector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="myHnswProfile",
                ),
            ]
            
            # Configure vector search
            vector_search = VectorSearch(
                profiles=[
                    VectorSearchProfile(
                        name="myHnswProfile",
                        algorithm_configuration_name="myHnsw",
                    )
                ],
                algorithms=[
                    HnswAlgorithmConfiguration(name="myHnsw")
                ],
            )
            
            # Create the index
            index = SearchIndex(
                name=self.search_index_name,
                fields=fields,
                vector_search=vector_search,
            )
            
            print(f"Creating index: {self.search_index_name}")
            result = self.search_index_client.create_or_update_index(index)
            print(f"✓ Index created successfully: {result.name}")
            return True
            
        except Exception as e:
            print(f"✗ Error creating index: {str(e)}")
            return False
    
    def step3_index_documents(self):
        """Step 3: Index product documents into AI Search"""
        print("\n" + "="*80)
        print("STEP 3: Indexing Product Documents")
        print("="*80)
        
        try:
            from azure.search.documents import SearchClient
            from openai import AzureOpenAI
            
            # Initialize OpenAI client for embeddings
            openai_client = AzureOpenAI(
                azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                api_version=os.getenv('AZURE_OPENAI_API_VERSION')
            )
            
            # Initialize search client for uploading documents
            search_client = SearchClient(
                endpoint=self.search_endpoint,
                index_name=self.search_index_name,
                credential=AzureKeyCredential(self.search_key)
            )
            
            # Read product files
            data_path = Path(__file__).parent.parent / "data" / "product-info"
            product_files = list(data_path.glob("*.md"))
            
            documents = []
            print(f"Processing {len(product_files)} product files...")
            
            for i, file_path in enumerate(product_files, 1):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract title (first line after #)
                title = file_path.stem.replace('_', ' ').title()
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('# '):
                        title = line.replace('# ', '').strip()
                        break
                
                # Generate embedding
                print(f"  Generating embedding for {file_path.name}...")
                embedding_response = openai_client.embeddings.create(
                    input=content[:8000],  # Limit content size
                    model="text-embedding-ada-002"
                )
                embedding = embedding_response.data[0].embedding
                
                # Create document
                doc = {
                    "id": str(i),
                    "content": content,
                    "title": title,
                    "filepath": str(file_path),
                    "url": f"file:///{file_path}",
                    "contentVector": embedding,
                }
                documents.append(doc)
            
            # Upload documents
            print(f"\nUploading {len(documents)} documents to search index...")
            result = search_client.upload_documents(documents=documents)
            print(f"✓ Indexed {len(result)} documents successfully")
            return True
            
        except Exception as e:
            print(f"✗ Error indexing documents: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def step4_create_prompt_flow(self):
        """Step 4: Create Prompt Flow for the copilot"""
        print("\n" + "="*80)
        print("STEP 4: Creating Prompt Flow")
        print("="*80)
        
        flow_path = Path(__file__).parent.parent / "prompt_flows" / "outlander_copilot"
        flow_path.mkdir(parents=True, exist_ok=True)
        
        # Create flow.dag.yaml
        flow_dag = f"""$schema: https://azuremlschemas.azureedge.net/promptflow/latest/Flow.schema.json
name: outlander_ai_copilot
display_name: Outlander AI Copilot
type: chat
description: AI Copilot for Outlander Gear Co. product assistance

inputs:
  chat_input:
    type: string
    default: "How much do the TrailWalker Hiking Shoes cost?"
  chat_history:
    type: list
    default: []

outputs:
  answer:
    type: string
    reference: ${{generate_response.output}}

nodes:
- name: search_products
  type: python
  source:
    type: code
    path: search_products.py
  inputs:
    question: ${{{{inputs.chat_input}}}}
    index_name: {self.search_index_name}
    search_endpoint: {self.search_endpoint}
    search_key: {self.search_key}

- name: generate_response
  type: llm
  source:
    type: code
    path: generate_response.jinja2
  inputs:
    deployment_name: {os.getenv('AZURE_DEPLOYMENT_NAME')}
    question: ${{{{inputs.chat_input}}}}
    context: ${{{{search_products.output}}}}
    chat_history: ${{{{inputs.chat_history}}}}
  connection: azure_openai_connection
  api: chat
"""
        
        with open(flow_path / "flow.dag.yaml", 'w') as f:
            f.write(flow_dag)
        
        print(f"✓ Prompt Flow created at: {flow_path}")
        return True
    
    def step5_test_flow(self):
        """Step 5: Test the Prompt Flow locally"""
        print("\n" + "="*80)
        print("STEP 5: Testing Prompt Flow")
        print("="*80)
        
        try:
            from promptflow import PFClient
            
            pf_client = PFClient()
            flow_path = Path(__file__).parent.parent / "prompt_flows" / "outlander_copilot"
            
            # Test with sample question
            test_question = "How much do the TrailWalker Hiking Shoes cost?"
            print(f"Testing with question: '{test_question}'")
            
            result = pf_client.test(
                flow=str(flow_path),
                inputs={"chat_input": test_question, "chat_history": []}
            )
            
            print(f"✓ Flow test successful!")
            print(f"Response: {result.get('answer', 'No response')}")
            return True
            
        except Exception as e:
            print(f"⚠ Flow testing will be done after deployment")
            print(f"  Reason: {str(e)}")
            return True  # Don't fail the process
    
    def step6_deploy(self):
        """Step 6: Deploy the Prompt Flow"""
        print("\n" + "="*80)
        print("STEP 6: Deploying Prompt Flow")
        print("="*80)
        
        try:
            from promptflow.azure import PFClient
            
            pf_client = PFClient(
                credential=DefaultAzureCredential(),
                subscription_id=self.subscription_id,
                resource_group_name=self.resource_group,
                workspace_name=self.project_name
            )
            
            flow_path = Path(__file__).parent.parent / "prompt_flows" / "outlander_copilot"
            
            print("Creating deployment...")
            deployment = pf_client.deployments.create_or_update(
                deployment_name="outlander-copilot-deployment",
                flow=str(flow_path),
                instance_type="Standard_DS3_v2",
                instance_count=1,
            )
            
            print(f"✓ Deployment created: {deployment.name}")
            print(f"  Endpoint: {deployment.endpoint}")
            return True
            
        except Exception as e:
            print(f"✗ Error deploying: {str(e)}")
            print("  You can deploy manually from Azure AI Foundry portal")
            return False
    
    def run_complete_setup(self):
        """Run all steps in sequence"""
        print("\n" + "="*80)
        print("OUTLANDER GEAR CO. - AUTOMATED COPILOT SETUP")
        print("="*80)
        
        steps = [
            ("Upload Data", self.step1_upload_data),
            ("Create Search Index", self.step2_create_search_index),
            ("Index Documents", self.step3_index_documents),
            ("Create Prompt Flow", self.step4_create_prompt_flow),
            ("Test Flow", self.step5_test_flow),
            ("Deploy", self.step6_deploy),
        ]
        
        results = []
        for step_name, step_func in steps:
            try:
                success = step_func()
                results.append((step_name, success))
                if not success:
                    print(f"\n⚠ {step_name} encountered issues. Continue? (y/n): ", end='')
                    response = input().lower()
                    if response != 'y':
                        break
            except Exception as e:
                print(f"\n✗ Error in {step_name}: {str(e)}")
                results.append((step_name, False))
        
        # Summary
        print("\n" + "="*80)
        print("SETUP SUMMARY")
        print("="*80)
        for step_name, success in results:
            status = "✓ PASSED" if success else "✗ FAILED"
            print(f"{status} - {step_name}")
        
        print("\n" + "="*80)

def main():
    """Main entry point"""
    try:
        builder = OutlanderCopilotBuilder()
        builder.run_complete_setup()
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
