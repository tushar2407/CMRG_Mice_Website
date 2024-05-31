# !pip install paramiko

import os
import paramiko

# Configuration
local_folder = '/path/to/local/folder'
remote_folder = '/path/to/remote/folder'
remote_host = 'remote.desktop.ip.address'
remote_port = 22  # default SSH port
username = 'your_username'
password = 'your_password'  # Consider using key-based authentication for better security

def upload_files(local_folder, remote_folder):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to the remote server
        ssh.connect(remote_host, port=remote_port, username=username, password=password)
        sftp = ssh.open_sftp()
        
        # Ensure the remote folder exists
        try:
            sftp.stat(remote_folder)
        except FileNotFoundError:
            sftp.mkdir(remote_folder)
        
        # Walk through the local folder
        for root, dirs, files in os.walk(local_folder):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_folder)
                remote_path = os.path.join(remote_folder, relative_path)
                
                remote_dir = os.path.dirname(remote_path)
                try:
                    sftp.stat(remote_dir)
                except FileNotFoundError:
                    sftp.makedirs(remote_dir)
                
                print(f'Uploading {local_path} to {remote_path}')
                sftp.put(local_path, remote_path)
        
        print('File transfer completed successfully.')
    
    except Exception as e:
        print(f'An error occurred: {e}')
    
    finally:
        sftp.close()
        ssh.close()

if __name__ == '__main__':
    upload_files(local_folder, remote_folder)
