import paramiko
import hashlib
import os
from pathlib import Path
import stat
import time

hostname = "192.168.100.200"
port = 22
username = "TENG"
password = "raspberry"

ruta_remota = "/var/opt/codesys/PlcLogic/FTP_Folder"
current_path = str(Path("__file__").resolve().parent)

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add unknown hosts

def shutdown():
    stdin, stdout, stderr = ssh.exec_command("sudo poweroff")
    
def reboot():
    stdin, stdout, stderr = ssh.exec_command("sudo reboot")

def stop_codesys():
    
    stdin, stdout, stderr = ssh.exec_command("sudo service codesyscontrol stop")
    
    # Wait until command finishes
    stdout.channel.recv_exit_status()
    
    # Check command error
    error = stderr.read().decode()
    if error != '':
        raise Exception(error)
    else:
        print("codesyscontrol stopped")
    
def start_codesys():
    
    stdin, stdout, stderr = ssh.exec_command("sudo service codesyscontrol start")
    
    # Wait until command finishes
    stdout.channel.recv_exit_status()
    
    # Check command error
    error = stderr.read().decode()
    if error != '':
        raise Exception(error)
    else:
        print("codesyscontrol started")
    
    
def check_file_integrity(local_path, remote_path):
    
    # Important, els noms de fitxers han d'anar entre "" 
    # ja que les () en la terminal es consideren per fer subprocessos o arrays
    stdin, stdout, stderr = ssh.exec_command("sha256sum " + f"'{remote_path}'")
    
    # Wait until command finishes
    stdout.channel.recv_exit_status()
    
    # Check command error
    error = stderr.read().decode()
    if error != '':
        raise Exception(error)
        
    sha256sum_remote = stdout.read().decode().split("  ")[0]

    with open(local_path, "rb") as file:
        data = file.read()
        sha256_local = hashlib.sha256(data).hexdigest()
    
    print("Remote SHA256:", sha256sum_remote)
    print("Local SHA256:", sha256_local)
    
    if sha256sum_remote == sha256_local:
        print("File integrity success, hash match!")
        return True
    else:
        print("File integrity failed, hash doesn't match")
        return False
    
def upload_file(local_path, remote_path):
    
    print(f"Uploading file from {local_path} to {remote_path}")
    
    # Loading into /tmp/ because sftp doesn't have sudo privilegies
    file_name = os.path.split(local_path)[-1]
    sftp.put(local_path, f"/tmp/{file_name}")
    
    # Move from /tmp/ to the remote_path using sudo
    stdin, stdout, stderr = ssh.exec_command(f"sudo mv '/tmp/{file_name}' '{remote_path}'")
    
    # Wait until command finishes
    stdout.channel.recv_exit_status()
    
    # Check command error
    error = stderr.read().decode()
    if error != '':
        raise Exception(error)
        
    # Check file integrity
    if check_file_integrity(local_path, remote_path):
        print("File Successfully uploaded")
        return True
    else:
        print("Error when uploading the file")
        return False
        
def download_file(remote_path, local_path, max_retries = 5):
    attempt = 0
    while attempt < max_retries:
        print(f'\nDownloading file: {remote_path}')
        sftp.get(remote_path, local_path)
        
        # Check file integrity
        if check_file_integrity(local_path, remote_path):
            print("File Successfully downloaded")
            return
        else:
            print(f"Retrying in 1 second, attempt = {attempt}")
            attempt += 1
            time.sleep(1)

    raise Exception("Error while trying to download a file")

def download_folder(remote_path, local_path):
    os.makedirs(local_path, exist_ok=True)  # Don't raise error if it exist
            
    for item in sftp.listdir_attr(remote_path):
        
        remote_item = remote_path + '/' + item.filename
        local_item = os.path.join(local_path, item.filename)
        
        if stat.S_ISDIR(item.st_mode):
            # If it is a folder, do recursive call
            download_folder(sftp, remote_item, local_item)
        else:
            # If it is a file, download it
            download_file(remote_item, local_item)

def remove_file(remote_path):
    
    stdin, stdout, stderr = ssh.exec_command(f"sudo rm -v '{remote_path}'")
    
    # Wait until command finishes
    stdout.channel.recv_exit_status()
    
    # Deleted file:
    deleted_file = stdout.read().decode()
    print("File to remove:", deleted_file)
    
    # Check command error
    error = stderr.read().decode()
    if error != '':
        raise Exception(error)
    else:
        print("File successfully removed")
        
def remove_folder(remote_path):
    
    stdin, stdout, stderr = ssh.exec_command(f"sudo rm -rf -v '{remote_path}'")
    
    # Wait until command finishes
    stdout.channel.recv_exit_status()
    
    # Deleted file:
    deleted_items = stdout.read().decode()
    print("Folder and files to remove:")
    print(deleted_items)
    
    # Check command error
    error = stderr.read().decode()
    if error != '':
        raise Exception(error)
    else:
        print("Files and folders successfully removed")
        
def remove_files_with_extension(remote_folder_path, extension = ".csv"):

    stdin, stdout, stderr = ssh.exec_command(f"sudo find {remote_folder_path} -type f -name '*{extension}' -print -delete")

    # Wait until command finishes
    stdout.channel.recv_exit_status()

    # Deleted files:
    deleted_files = stdout.read().decode()
    print("Files to remove:")
    print(deleted_files)

    # Check command error
    error = stderr.read().decode()
    if error != '':
        raise Exception(error)
    else:
        if deleted_files:
            print("Files successfully removed")
        else:
            print("There are no files to remove")
            
def get_elements(folder_path):
    # Get elements from a path
    list_elements = sftp.listdir(folder_path)
    return list_elements

def get_files(folder_path):
    # Obtenir nomes fitxers, excloure les carpetes
    entries = sftp.listdir_attr(ruta_remota)
    path_files = [e.filename for e in entries if stat.S_ISREG(e.st_mode)]
    return path_files

def get_folders(folder_path):
    # Obtenir nomes carpetes
    entries = sftp.listdir_attr(ruta_remota)
    path_folders = [e.filename for e in entries if stat.S_ISDIR(e.st_mode)]
    return path_folders
    

try:
    # Connect to the host
    ssh.connect(hostname, port=port, username=username, password=password)
    
    # Iniciar sesión SFTP
    sftp = ssh.open_sftp()
    
    # Reset Codesys
    stop_codesys()
    start_codesys()

    # Close the connection
    # ssh.close()
    # sftp.close()

except paramiko.AuthenticationException:
    print("Authentication failed.")
except paramiko.SSHException as e:
    print(f"SSH error: {e}")
except Exception as e:
    print(f"Other error: {e}")