import paramiko


class RPIClientSSH:
    """
    Used for connecting to RPI as SSH client
    """

    def __init__(self, host='MDPGroup29', user='MDPGrp29', password='2024Grp29'):
        self.client = paramiko.SSHClient()
        self.host = host
        self.user = user
        self.password = password

    def connect(self):
        try:
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.host, username=self.user, password=self.password)
            print("Connected to Raspberry Pi via SSH")
        except Exception as e:
            print(f"Error connecting to Raspberry Pi: {e}")

    def send_message(self, obj):
        try:
            for command in obj:
                stdin, stdout, stderr = self.client.exec_command(command)
                print(f"Command: {command}\nOutput: {stdout.read().decode('utf-8')}")
        except Exception as e:
            print(f"Error sending message to Raspberry Pi: {e}")

    def close(self):
        self.client.close()
