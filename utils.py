import os

def load_kernel_modules():
    os.system('modprobe sctp')
    os.system('modprobe dccp')