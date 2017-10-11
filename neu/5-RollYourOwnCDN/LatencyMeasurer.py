import subprocess


p = subprocess.Popen(["ping.exe","www.google.com"], stdout = subprocess.PIPE)
print p.communicate()[0]