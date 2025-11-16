# Outlander Copilot Deployment Commands

## Prerequisites
- Azure CLI installed: https://aka.ms/azure-cli
- Logged in to Azure: `az login`
- ML extension installed: `az extension add -n ml`

## Configuration
$SUBSCRIPTION_ID = "05e7b074-305c-48d8-9bd0-ce5305cd027c"
$RESOURCE_GROUP = "rg-rodolfolermacontreras-7270_ai"
$WORKSPACE = "outlander-hub"
$LOCATION = "eastus2"

## Step 1: Create Managed Online Endpoint
az ml online-endpoint create `
  --file deployment/endpoint.yaml `
  --resource-group $RESOURCE_GROUP `
  --workspace-name $WORKSPACE `
  --subscription $SUBSCRIPTION_ID

## Step 2: Create Deployment
az ml online-deployment create `
  --file deployment/deployment.yaml `
  --resource-group $RESOURCE_GROUP `
  --workspace-name $WORKSPACE `
  --subscription $SUBSCRIPTION_ID `
  --all-traffic

## Step 3: Verify Deployment
az ml online-endpoint show `
  --name outlander-copilot-endpoint `
  --resource-group $RESOURCE_GROUP `
  --workspace-name $WORKSPACE

## Step 4: Get Endpoint Keys
az ml online-endpoint get-credentials `
  --name outlander-copilot-endpoint `
  --resource-group $RESOURCE_GROUP `
  --workspace-name $WORKSPACE

## Step 5: Test Deployment
$ENDPOINT_URI = az ml online-endpoint show `
  --name outlander-copilot-endpoint `
  --resource-group $RESOURCE_GROUP `
  --workspace-name $WORKSPACE `
  --query scoring_uri -o tsv

$API_KEY = az ml online-endpoint get-credentials `
  --name outlander-copilot-endpoint `
  --resource-group $RESOURCE_GROUP `
  --workspace-name $WORKSPACE `
  --query primaryKey -o tsv

# Test with curl or PowerShell
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $API_KEY"
}

$body = @{
    chat_input = "Which tent is the most waterproof?"
    chat_history = @()
} | ConvertTo-Json

Invoke-RestMethod -Uri $ENDPOINT_URI -Method Post -Headers $headers -Body $body

## Clean Up (After Testing)
# Delete deployment to avoid charges
az ml online-endpoint delete `
  --name outlander-copilot-endpoint `
  --resource-group $RESOURCE_GROUP `
  --workspace-name $WORKSPACE `
  --yes `
  --no-wait
