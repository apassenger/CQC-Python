#from SimulaQron.general.hostConfig import *
#from SimulaQron.cqc.backend.cqcHeader import *
#from SimulaQron.cqc.pythonLib.cqc import *
from cqc.pythonLib import CQCConnection, qubit

import random
import numpy
import pickle
import os
###################################
#
# Functions
#
def ACKSend(name, target, data):
    name.sendClassical(target, data)
    while bytes(name.recvClassical(msg_size=3)) != b'ACK':
        pass
                
def ACKRecv(name, target):
    data = list(name.recvClassical())
    name.sendClassical(target, list(b'ACK'))
    return data

def receive_quantum_signature(name, target, N, L):
    while bytes(ACKRecv(name, target)) != b'ACK':
        pass
    USE={}
    for k in range (0,pow(2,N)):
        USE[k]=[]
        for l in range (0,L):
            c=0
            q=name.recvQubit()
            j=random.randint(0,1)
            if j==0:
                m=q.measure()
                c=1
                if m==0:
                    USE[k].append(1)
                elif m==1:
                    USE[k].append(0)
            elif j==1:
                q.H()
                m=q.measure()
                c=1
                if m==0:
                    USE[k].append(3)
                elif m==1:
                    USE[k].append(2)
            ACKSend(name, target, list(b'ACK'))
    return USE

###################################
#
# Main
#
def main():
    
    # Get parameters
    config=numpy.loadtxt("config.txt")
    L=int(config[0])
    N=int(config[1])
    
    # Delete any existing USE files
    if os.path.isfile("B0.txt"):
        os.remove("B0.txt")
    if os.path.isfile("B1.txt"):
        os.remove("B1.txt")

    # Initialise CQC connection
    with CQCConnection("Bob") as Bob:
    
        # Receive public (quantum) key from Alice
        USE=receive_quantum_signature(Bob, "Alice", N, L)
        B0=open("B0.txt", "a+")
        B1=open("B1.txt", "a+")

        # Write USE to file
        for item in USE[0]:
            B0.write("%s " % item)
        for item in USE[1]:
            B1.write("%s " % item)

        B0.close()
        B0.close()

        # Inform Alice of completed symmetrisation
        while bytes(ACKRecv(Bob, "Alice")) != b'ACK':
            pass

main()
