
def get_IP():

    import subprocess
    process = subprocess.Popen(['hostname', '-I'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.strip()
