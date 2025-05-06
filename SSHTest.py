import paramiko
import stat

hostname = "192.168.100.200"
port = 22
username = "TENG"
password = "raspberry"

ruta_remota = "/var/opt/codesys/PlcLogic/FTP_Folder"
ruta_local = "archivo_descargado.txt"

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add unknown hosts

# Important, els noms de fitxers han d'anar entre "" 
# ja que les () en la terminal es consideren per fer subprocessos o arrays

def stop_codesys():
    stdin, stdout, stderr = ssh.exec_command("sudo service codesyscontrol stop")
    # Esperar a que termine el comando
    exit_status = stdout.channel.recv_exit_status()
    print("codesyscontrol stopped")
    
def start_codesys():
    stdin, stdout, stderr = ssh.exec_command("sudo service codesyscontrol start")
    # Esperar a que termine el comando
    exit_status = stdout.channel.recv_exit_status()
    print("codesyscontrol started")
    
try:
    # Connect to the host
    ssh.connect(hostname, port=port, username=username, password=password)
    
    # Iniciar sesión SFTP
    sftp = ssh.open_sftp()
    lista_ficheros = sftp.listdir(ruta_remota)
    # sftp.get(ruta_remota + "/" + lista_ficheros[0], "datafile.csv")  # Descarregar fitxer al PC
    
    # Obtenir nomes fitxers, excloure les carpetes
    entradas = sftp.listdir_attr(ruta_remota)
    solo_archivos = [e.filename for e in entradas if stat.S_ISREG(e.st_mode)]

    # Run a command
    # stdin, stdout, stderr = ssh.exec_command("ls -l /home/TENG")
    # print("Output:")
    # print(stdout.read().decode())
    
    # stop_codesys()
    # start_codesys()

    # Close the connection
    # ssh.close()
    # sftp.close()
except paramiko.AuthenticationException:
    print("Authentication failed.")
except paramiko.SSHException as e:
    print(f"SSH error: {e}")
except Exception as e:
    print(f"Other error: {e}")
