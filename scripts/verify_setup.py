"""
Verification and Testing Script for Outlander Gear Co. Copilot
This script verifies your Azure configuration and tests the GPT-4o deployment.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")

def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    """Print info message."""
    print(f"  {text}")

def check_environment_file():
    """Check if .env file exists and is configured."""
    print_header("STEP 1: Checking Environment Configuration")
    
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print_error(".env file not found!")
        return False
    
    print_success(".env file found")
    
    # Load environment variables
    load_dotenv(env_path)
    
    # Check required variables
    required_vars = {
        'AZURE_OPENAI_ENDPOINT': 'Azure OpenAI Endpoint',
        'AZURE_OPENAI_API_KEY': 'Azure OpenAI API Key',
        'AZURE_DEPLOYMENT_NAME': 'Deployment Name',
        'AZURE_AI_PROJECT_NAME': 'Project Name',
        'AZURE_SEARCH_SERVICE_NAME': 'AI Search Service Name'
    }
    
    all_configured = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and 'your_' not in value.lower():
            print_success(f"{description}: Configured")
            print_info(f"  Value: {value[:50]}..." if len(value) > 50 else f"  Value: {value}")
        else:
            print_warning(f"{description}: NOT configured or placeholder value")
            all_configured = False
    
    # Check AI Search Key
    search_key = os.getenv('AZURE_SEARCH_API_KEY')
    if search_key and 'your_' not in search_key.lower():
        print_success("AI Search API Key: Configured")
    else:
        print_warning("AI Search API Key: NOT configured - You need to add this from Azure Portal")
        print_info("  Go to Azure Portal → AI Search → projectaisearchfree → Keys")
        all_configured = False
    
    return all_configured

def check_data_files():
    """Check if data files are present."""
    print_header("STEP 2: Checking Data Files")
    
    data_path = Path(__file__).parent.parent / "data"
    
    # Check product-info folder
    product_info_path = data_path / "product-info"
    if product_info_path.exists():
        product_files = list(product_info_path.glob("*.md"))
        print_success(f"Product data folder found with {len(product_files)} files")
        print_info(f"  Location: {product_info_path}")
    else:
        print_error("Product data folder not found!")
        return False
    
    # Check customer-info folder
    customer_info_path = data_path / "customer-info"
    if customer_info_path.exists():
        customer_files = list(customer_info_path.glob("*.md"))
        print_success(f"Customer data folder found with {len(customer_files)} files")
        print_info(f"  Location: {customer_info_path}")
    else:
        print_warning("Customer data folder not found (optional)")
    
    return True

def check_evaluation_dataset():
    """Check if evaluation dataset exists."""
    print_header("STEP 3: Checking Evaluation Dataset")
    
    eval_path = Path(__file__).parent.parent / "evaluation" / "evaluation_dataset.jsonl"
    if eval_path.exists():
        with open(eval_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print_success(f"Evaluation dataset found with {len(lines)} test questions")
        print_info(f"  Location: {eval_path}")
        return True
    else:
        print_error("Evaluation dataset not found!")
        return False

def test_openai_connection():
    """Test connection to Azure OpenAI."""
    print_header("STEP 4: Testing Azure OpenAI Connection")
    
    try:
        from openai import AzureOpenAI
        
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        deployment = os.getenv('AZURE_DEPLOYMENT_NAME')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION')
        
        if not all([endpoint, api_key, deployment]):
            print_error("Missing OpenAI configuration in .env file")
            return False
        
        print_info(f"Connecting to: {endpoint}")
        print_info(f"Deployment: {deployment}")
        
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        print_info("Sending test request...")
        
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for an outdoor gear company."},
                {"role": "user", "content": "Say 'Connection successful!' if you receive this."}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        print_success(f"Connection successful! Model responded: {result}")
        print_info(f"  Tokens used: {response.usage.total_tokens}")
        return True
        
    except ImportError:
        print_warning("OpenAI library not installed. Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print_error(f"Connection failed: {str(e)}")
        return False

def check_folders():
    """Check if required folders exist."""
    print_header("STEP 5: Checking Project Structure")
    
    base_path = Path(__file__).parent.parent
    required_folders = {
        'data': 'Data files',
        'evaluation': 'Evaluation datasets',
        'screenshots': 'Screenshots for submission',
        'scripts': 'Utility scripts',
        'prompt_flows': 'Prompt Flow configurations'
    }
    
    all_exist = True
    for folder, description in required_folders.items():
        folder_path = base_path / folder
        if folder_path.exists():
            print_success(f"{description} folder exists: {folder}/")
        else:
            print_warning(f"{description} folder missing: {folder}/")
            all_exist = False
    
    return all_exist

def display_next_steps():
    """Display next steps for the user."""
    print_header("NEXT STEPS")
    
    steps = [
        ("1. Get AI Search Admin Key", 
         "   Go to Azure Portal → AI Search → projectaisearchfree → Keys",
         "   Copy Primary admin key and add to .env file"),
        
        ("2. Upload Data to Azure AI Foundry",
         "   Go to https://ai.azure.com → outlander-copilot project",
         "   Data tab → + New Data → Upload files from data/product-info/"),
        
        ("3. Create AI Search Index",
         "   Indexes tab → + New Index",
         "   Source: Your uploaded data",
         "   Embeddings: gpt-4o deployment"),
        
        ("4. Build Prompt Flow",
         "   Chat playground → Add your index",
         "   Click 'Prompt Flow' → Name: outlander-ai-copilot"),
        
        ("5. Test the Copilot",
         "   Start compute session",
         "   Test with questions from evaluation_dataset.jsonl",
         "   Take screenshots!"),
        
        ("6. Run Evaluations",
         "   Automated: Upload evaluation_dataset.jsonl",
         "   Manual: Test and provide feedback",
         "   Capture evaluation results"),
        
        ("7. Deploy",
         "   Deploy button in Prompt Flow",
         "   Name: outlander-copilot-deployment",
         "   Capture deployment confirmation")
    ]
    
    for step in steps:
        print(f"\n{GREEN}{step[0]}{RESET}")
        for line in step[1:]:
            print(f"  {line}")

def main():
    """Main verification function."""
    print(f"\n{BLUE}╔{'═' * 78}╗{RESET}")
    print(f"{BLUE}║{'OUTLANDER GEAR CO. - COPILOT PROJECT VERIFICATION'.center(78)}║{RESET}")
    print(f"{BLUE}╚{'═' * 78}╝{RESET}")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run all checks
    checks = [
        ("Environment Configuration", check_environment_file),
        ("Data Files", check_data_files),
        ("Evaluation Dataset", check_evaluation_dataset),
        ("Project Structure", check_folders),
        ("OpenAI Connection", test_openai_connection)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Error during {name} check: {str(e)}")
            results.append((name, False))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED or INCOMPLETE")
    
    print(f"\n{BLUE}Overall: {passed}/{total} checks passed{RESET}\n")
    
    if passed == total:
        print_success("All checks passed! You're ready to proceed with Azure AI Foundry setup.")
    else:
        print_warning("Some checks failed. Please review the issues above and fix them.")
    
    # Display next steps
    display_next_steps()
    
    print(f"\n{BLUE}{'=' * 80}{RESET}\n")

if __name__ == "__main__":
    main()
