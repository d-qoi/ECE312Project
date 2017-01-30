'''
Created on Jan 30, 2017

@author: hirschag
'''
import socket
import re
from packets import RHP, RHMP

def prettyPrintRHP(data):
    print(
'''-----
RHP message:
    type:     %s
    Src port: %s
    dst port: %s
    length:   %s
    payload:  %s
    checksum: %s
-----''' % (data['type'], data['srcPort'], data['dstPort'], data['length'], data['payload'], data['checksum']))
    
def prettyPrintRHMP(data):
    print(
'''-----
RHMP message
    type:    %s
    commID:  %s
    length:  %s
    payload: %s
-----''' % (data['type'], data['commID'], data['length'], data['payload']))


if __name__ == '__main__':
    IPAddr = '137.112.38.47'
    PORT = 1874
    
    HOST = ''
    
    srcPort = 1125
    dstPort = 105
    commID = 312
    
    rhp = RHP(dstPort, srcPort)
    rhmp = RHMP(commID)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print('starting')
    try:
        sock.bind((HOST, 1125))
        print('socket bound')
    except:
        print('failed')
        raise
    
    #message = rhp.sendCAM('hello')
    message = rhp.sendRHMP(rhmp.sendID_Request())
    
    print('Message before decoding: %s' % message)
    prettyPrintRHP(rhp.decode(message))
    prettyPrintRHMP(rhmp.decode(rhp.decode(message)['payload']))
    #message = message[:-4] + '0000'
    toSend = bytes.fromhex(message)
    print(toSend)
    try:
        sock.sendto(toSend, (IPAddr, PORT))
        print('message sent')
    except:
        print('failed to send message')
        raise
    
    data, addr = sock.recvfrom(1024)
    print('Data: %s' % data)
    print('addr: %s' % str(addr))
    decoded = rhp.decode(data.hex())
    print('message before decodding: %s ' % data.hex())
    prettyPrintRHP(decoded)
    payload = ''.join([chr(int(x,16)) for x in re.findall('..', decoded['payload'])])
    print(payload)