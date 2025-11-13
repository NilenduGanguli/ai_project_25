"""
Testing script for Image Data Extractor Service

This script demonstrates the complete workflow:
1. Upload passport.pdf to generate schema
2. Retrieve the generated schema
3. Approve the schema
4. Test extraction with the approved schema
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8005"
TEST_PDF_PATH = Path("test/Passport.pdf")

# Colors for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")


def print_info(text):
    """Print info message"""
    print(f"{YELLOW}→ {text}{RESET}")


def check_service_health():
    """Check if the service is running"""
    print_header("Checking Service Health")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print_success("Service is healthy and running")
            return True
        else:
            print_error(f"Service returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Cannot connect to service: {e}")
        print_info("Make sure the service is running: docker-compose up -d")
        return False


def check_test_file():
    """Check if test PDF exists"""
    print_header("Checking Test File")
    if not TEST_PDF_PATH.exists():
        print_error(f"Test file not found: {TEST_PDF_PATH}")
        return False
    
    file_size = TEST_PDF_PATH.stat().st_size / 1024  # KB
    print_success(f"Test file found: {TEST_PDF_PATH}")
    print_info(f"File size: {file_size:.2f} KB")
    return True


def generate_schema():
    """Step 1: Upload passport to generate schema"""
    print_header("Step 1: Generating Schema from Passport")
    
    try:
        with open(TEST_PDF_PATH, 'rb') as f:
            files = {'document': (TEST_PDF_PATH.name, f, 'application/pdf')}
            
            print_info("Uploading passport.pdf to /extract endpoint...")
            response = requests.post(
                f"{BASE_URL}/extract",
                files=files,
                timeout=300  # 5 minutes for schema generation
            )
        
        print_info(f"Response Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print_success("Schema generated successfully!")
            
            schema_id = data.get('schema_id')
            classification = data.get('classification', {})
            generated_schema = data.get('generated_schema', {})
            
            print_info(f"Schema ID: {schema_id}")
            print_info(f"Document Type: {classification.get('document_type')}")
            print_info(f"Country: {classification.get('country')}")
            print_info(f"Confidence: {classification.get('confidence')}")
            
            print("\nGenerated Schema Fields:")
            schema_fields = generated_schema.get('schema', {})
            for field_name, field_def in schema_fields.items():
                print(f"  • {field_name}: {field_def.get('type')} - {field_def.get('description')}")
            
            return schema_id, data
            
        elif response.status_code == 202:
            data = response.json()
            print_error("Schema already exists and is pending review")
            schema_id = data.get('schema_id')
            print_info(f"Existing Schema ID: {schema_id}")
            return schema_id, data
            
        elif response.status_code == 200:
            data = response.json()
            print_error("Active schema already exists - extraction was performed")
            print_info("Schema is already approved and active")
            schema_info = data.get('schema_used', {})
            print_info(f"Document Type: {schema_info.get('document_type')}")
            print_info(f"Country: {schema_info.get('country')}")
            print_info(f"Version: {schema_info.get('version')}")
            return None, data
            
        else:
            print_error(f"Failed to generate schema: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
            
    except requests.exceptions.Timeout:
        print_error("Request timed out - schema generation may take longer")
        return None, None
    except Exception as e:
        print_error(f"Error: {e}")
        return None, None


def get_all_schemas():
    """Retrieve all schemas"""
    print_header("Retrieving All Schemas")
    
    try:
        response = requests.get(f"{BASE_URL}/schemas", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            schemas = data.get('schemas', [])
            total = data.get('total_count', 0)
            
            print_success(f"Found {total} schema(s)")
            
            for schema in schemas:
                print(f"\n  Schema ID: {schema['id']}")
                print(f"  Type: {schema['document_type']} ({schema['country']})")
                print(f"  Status: {schema['status']}")
                print(f"  Version: {schema['version']}")
                print(f"  Created: {schema['created_at']}")
            
            return schemas
        else:
            print_error(f"Failed to retrieve schemas: {response.status_code}")
            return []
            
    except Exception as e:
        print_error(f"Error: {e}")
        return []


def approve_schema(schema_id):
    """Step 2: Approve the schema"""
    print_header("Step 2: Approving Schema")
    
    if not schema_id:
        print_error("No schema ID provided")
        return False
    
    try:
        print_info(f"Approving schema: {schema_id}")
        response = requests.put(
            f"{BASE_URL}/schemas/{schema_id}/approve",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Schema approved successfully!")
            
            schema_info = data.get('schema', {})
            print_info(f"Document Type: {schema_info.get('document_type')}")
            print_info(f"Country: {schema_info.get('country')}")
            print_info(f"Status: {schema_info.get('status')}")
            print_info(f"Version: {schema_info.get('version')}")
            
            deprecated_info = data.get('deprecated_schema')
            if deprecated_info:
                print_info(f"Previous version deprecated: v{deprecated_info.get('version')}")
            
            return True
        else:
            print_error(f"Failed to approve schema: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_extraction():
    """Step 3: Test extraction with approved schema"""
    print_header("Step 3: Testing Extraction with Approved Schema")
    
    try:
        with open(TEST_PDF_PATH, 'rb') as f:
            files = {'document': (TEST_PDF_PATH.name, f, 'application/pdf')}
            
            print_info("Uploading passport.pdf for extraction...")
            response = requests.post(
                f"{BASE_URL}/extract",
                files=files,
                timeout=300  # 5 minutes for extraction
            )
        
        print_info(f"Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Extraction successful!")
            
            # Display classification
            classification = data.get('classification', {})
            print(f"\n{YELLOW}Classification:{RESET}")
            print(f"  Document Type: {classification.get('document_type')}")
            print(f"  Country: {classification.get('country')}")
            print(f"  Confidence: {classification.get('confidence')}")
            
            # Display schema used
            schema_used = data.get('schema_used', {})
            print(f"\n{YELLOW}Schema Used:{RESET}")
            print(f"  Document Type: {schema_used.get('document_type')}")
            print(f"  Country: {schema_used.get('country')}")
            print(f"  Version: {schema_used.get('version')}")
            
            # Display extracted data
            extracted_data = data.get('data', {})
            print(f"\n{GREEN}Extracted Data:{RESET}")
            print(json.dumps(extracted_data, indent=2))
            
            return True
        else:
            print_error(f"Extraction failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def main():
    """Main testing workflow"""
    print_header("Image Data Extractor - Complete Workflow Test")
    
    # Check prerequisites
    if not check_service_health():
        return
    
    if not check_test_file():
        return
    
    print_info("Starting complete workflow test...")
    time.sleep(1)
    
    # Step 1: Generate schema
    schema_id, schema_data = generate_schema()
    
    if schema_id:
        time.sleep(2)
        
        # Check all schemas
        get_all_schemas()
        time.sleep(1)
        
        # Step 2: Approve schema
        if approve_schema(schema_id):
            time.sleep(2)
            
            # Step 3: Test extraction
            test_extraction()
    elif schema_data and schema_data.get('status') == 'extracted':
        # Schema already exists and is active
        print_info("\nSchema is already active. Testing extraction directly...")
        time.sleep(1)
        test_extraction()
    else:
        print_error("Could not proceed with workflow")
        return
    
    # Final summary
    print_header("Test Summary")
    print_success("All tests completed!")
    print_info("Check the output above for detailed results")


if __name__ == "__main__":
    main()
