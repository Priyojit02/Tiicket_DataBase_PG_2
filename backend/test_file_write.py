#!/usr/bin/env python3
"""
Test script to verify backend can write to frontend tickets2.ts file
"""
import json
import os
from datetime import datetime

def test_file_write():
    # Test data
    ticket_dict = {
        "id": 1001,
        "title": "Test ticket from backend",
        "description": "Testing file write functionality",
        "status": "Open",
        "priority": "Medium",
        "assignedTo": "Test User",
        "raisedBy": "System",
        "completionBy": datetime.now().date().isoformat(),
        "createdOn": datetime.now().date().isoformat(),
        "closedOn": None,
        "module": "MM",
        "tags": ["test"],
        "logs": [{
            "id": 1,
            "action": "ticket_created",
            "performedBy": "System Test",
            "timestamp": datetime.now().isoformat(),
            "details": "Test ticket creation"
        }],
        "comments": []
    }

    # Path to frontend data2.ts file
    frontend_data_file = os.path.join(os.path.dirname(__file__), "..", "frontend-up", "src", "data", "tickets2.ts")

    print(f"Writing to: {frontend_data_file}")
    print(f"File exists: {os.path.exists(frontend_data_file)}")

    try:
        # Read existing file
        with open(frontend_data_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print("File read successfully")

        # Replace placeholder with test ticket
        if '// LLM will add parsed tickets here' in content:
            new_content = content.replace('// LLM will add parsed tickets here', f"""
    {json.dumps(ticket_dict, indent=4)}""")

            with open(frontend_data_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print("Test ticket written successfully!")
            return True
        else:
            print("Placeholder not found - file may already have tickets")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_file_write()