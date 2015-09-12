ip_file = 'ip.txt'

def get_IP():

    import subprocess
    process = subprocess.Popen(['hostname', '-I'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.strip()

def write_current_IP():

    with open(ip_file, 'w') as f:
        f.writelines(get_IP())

def get_last_IP():

    with open(ip_file, 'r') as f:
        ip = f.readline()
        return ip

open(ip_file, 'w').close()
