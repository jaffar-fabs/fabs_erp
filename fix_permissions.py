#!/usr/bin/env python3
"""
Script to fix media directory permissions for FABS ERP
Run this script on your server to fix permission issues with file uploads
"""

import os
import sys
import stat
import subprocess

def fix_permissions():
    """Fix permissions for media directories"""
    
    # Get the current directory (should be the project root)
    project_root = os.getcwd()
    media_path = os.path.join(project_root, 'media')
    
    print(f"Fixing permissions for: {media_path}")
    
    if not os.path.exists(media_path):
        print(f"Creating media directory: {media_path}")
        try:
            os.makedirs(media_path, mode=0o755)
        except Exception as e:
            print(f"Error creating media directory: {e}")
            return False
    
    # Fix permissions for media directory and subdirectories
    try:
        # Set permissions for media directory
        os.chmod(media_path, 0o755)
        print(f"Set permissions for {media_path}")
        
        # Fix permissions for all subdirectories
        for root, dirs, files in os.walk(media_path):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    os.chmod(dir_path, 0o755)
                    print(f"Set permissions for directory: {dir_path}")
                except Exception as e:
                    print(f"Warning: Could not set permissions for {dir_path}: {e}")
            
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    os.chmod(file_path, 0o644)
                    print(f"Set permissions for file: {file_path}")
                except Exception as e:
                    print(f"Warning: Could not set permissions for {file_path}: {e}")
        
        print("Permission fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error fixing permissions: {e}")
        return False

def check_web_server_user():
    """Check and suggest the correct web server user"""
    
    print("\n=== Web Server User Check ===")
    
    # Common web server users
    common_users = ['www-data', 'apache', 'nginx', 'prime', 'ubuntu', 'ec2-user']
    
    for user in common_users:
        try:
            result = subprocess.run(['id', user], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Found user: {user}")
                print(f"User info: {result.stdout.strip()}")
                
                # Check if this user can write to media directory
                media_path = os.path.join(os.getcwd(), 'media')
                if os.path.exists(media_path):
                    try:
                        test_file = os.path.join(media_path, 'test_write.tmp')
                        with open(test_file, 'w') as f:
                            f.write('test')
                        os.remove(test_file)
                        print(f"✓ User {user} can write to media directory")
                    except Exception as e:
                        print(f"✗ User {user} cannot write to media directory: {e}")
                        print(f"  You may need to run: sudo chown -R {user}:{user} {media_path}")
                
                return user
        except Exception as e:
            continue
    
    print("Could not determine web server user automatically.")
    print("Please check your web server configuration.")
    return None

def main():
    """Main function"""
    print("FABS ERP - Media Directory Permission Fix")
    print("=" * 50)
    
    # Check web server user
    web_user = check_web_server_user()
    
    # Fix permissions
    print("\n=== Fixing Permissions ===")
    success = fix_permissions()
    
    if success:
        print("\n=== Summary ===")
        print("✓ Permissions have been fixed")
        print("✓ Try uploading files again")
        
        if web_user:
            print(f"\nIf you still have issues, try running:")
            print(f"sudo chown -R {web_user}:{web_user} media/")
            print(f"sudo chmod -R 755 media/")
    else:
        print("\n✗ Failed to fix permissions")
        print("You may need to run this script with sudo or contact your system administrator")

if __name__ == "__main__":
    main() 