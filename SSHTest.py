import paramiko
import stat
import hashlib
import os

hostname = "192.168.100.200"
port = 22
username = "TENG"
password = "raspberry"

ruta_remota = "/var/opt/codesys/PlcLogic/FTP_Folder"

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add unknown hosts

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
        
def download_file(remote_path, local_path):
    
    sftp.get(remote_path, local_path)
    
    # Check file integrity
    if check_file_integrity(local_path, remote_path):
        print("File Successfully downloaded")
        return True
    else:
        print("Error when downloading the file")
        return False
        
def remove_file(remote_path):
    
    stdin, stdout, stderr = ssh.exec_command(f"sudo rm '{remote_path}'")
    
    # Wait until command finishes
    stdout.channel.recv_exit_status()
    
    # Check command error
    error = stderr.read().decode()
    if error != '':
        raise Exception(error)
    else:
        print("File successfully removed")

try:
    # Connect to the host
    ssh.connect(hostname, port=port, username=username, password=password)
    
    # Iniciar sesión SFTP
    sftp = ssh.open_sftp()
    
    # Get elements from a path
    list_elements = sftp.listdir(ruta_remota)
    # sftp.get(ruta_remota + "/" + list_elements[0], "datafile.csv")  # Descarregar fitxer al PC
    
    # Obtenir nomes fitxers, excloure les carpetes
    entradas = sftp.listdir_attr(ruta_remota)
    path_files = [e.filename for e in entradas if stat.S_ISREG(e.st_mode)]
    
    # Reset Codesys
    stop_codesys()
    start_codesys()

    # Close the connection
    ssh.close()
    sftp.close()

except paramiko.AuthenticationException:
    print("Authentication failed.")
except paramiko.SSHException as e:
    print(f"SSH error: {e}")
except Exception as e:
    print(f"Other error: {e}")
