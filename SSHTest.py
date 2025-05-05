import paramiko

hostname = "192.168.100.200"
port = 22
username = "TENG"
password = "raspberry"

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add unknown hosts

try:
    # Connect to the host
    ssh.connect(hostname, port=port, username=username, password=password)

    # Run a command
    # stdin, stdout, stderr = ssh.exec_command("ls -l /home/TENG")
    # print("Output:")
    # print(stdout.read().decode())
    
    stdin, stdout, stderr = ssh.exec_command("sudo service codesyscontrol stop")
    # Esperar a que termine el comando
    exit_status = stdout.channel.recv_exit_status()  # Esto bloquea hasta que el comando 
    print("codesyscontrol stopped")
    
    stdin, stdout, stderr = ssh.exec_command("sudo service codesyscontrol start")
    # Esperar a que termine el comando
    exit_status = stdout.channel.recv_exit_status()  # Esto bloquea hasta que el comando 
    print("codesyscontrol started")

    # Close the connection
    # ssh.close()
except paramiko.AuthenticationException:
    print("Authentication failed.")
except paramiko.SSHException as e:
    print(f"SSH error: {e}")
except Exception as e:
    print(f"Other error: {e}")
