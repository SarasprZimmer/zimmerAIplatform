#!/usr/bin/env python3
"""
Fix Table Ownership Issues
This script transfers ownership of all tables to the zimmer user
"""

import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False

def fix_table_ownership():
    """Fix table ownership for zimmer user"""
    print("🔧 Fixing table ownership...")
    
    # Get list of all tables
    get_tables_cmd = """sudo -u postgres psql -d zimmer -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';" """
    
    try:
        result = subprocess.run(get_tables_cmd, shell=True, check=True, capture_output=True, text=True)
        tables = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        
        print(f"📋 Found {len(tables)} tables to fix ownership for")
        
        for table in tables:
            if table:
                # Transfer ownership of table
                transfer_cmd = f"sudo -u postgres psql -d zimmer -c \"ALTER TABLE {table} OWNER TO zimmer;\""
                run_command(transfer_cmd, f"Transferring ownership of {table}")
                
                # Grant all privileges on table
                grant_cmd = f"sudo -u postgres psql -d zimmer -c \"GRANT ALL PRIVILEGES ON TABLE {table} TO zimmer;\""
                run_command(grant_cmd, f"Granting privileges on {table}")
        
        # Also fix sequences
        get_sequences_cmd = """sudo -u postgres psql -d zimmer -t -c "SELECT sequencename FROM pg_sequences WHERE schemaname = 'public';" """
        try:
            result = subprocess.run(get_sequences_cmd, shell=True, check=True, capture_output=True, text=True)
            sequences = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            
            for sequence in sequences:
                if sequence:
                    # Transfer ownership of sequence
                    transfer_seq_cmd = f"sudo -u postgres psql -d zimmer -c \"ALTER SEQUENCE {sequence} OWNER TO zimmer;\""
                    run_command(transfer_seq_cmd, f"Transferring ownership of sequence {sequence}")
                    
                    # Grant all privileges on sequence
                    grant_seq_cmd = f"sudo -u postgres psql -d zimmer -c \"GRANT ALL PRIVILEGES ON SEQUENCE {sequence} TO zimmer;\""
                    run_command(grant_seq_cmd, f"Granting privileges on sequence {sequence}")
        except:
            print("⚠️  No sequences found or error getting sequences")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting table list: {e.stderr.strip()}")
        return False
    
    print("✅ Table ownership fixed")
    return True

def main():
    """Main fix function"""
    print("🚀 Fixing Table Ownership Issues")
    print("=" * 50)
    
    fix_table_ownership()
    
    print("=" * 50)
    print("🎉 Table ownership issues fixed!")

if __name__ == "__main__":
    main()
