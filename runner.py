'''
Created on Jan 30, 2017

@author: hirschag
'''
import socket
import re
from time import sleep
from packets import RHP, RHMP

IPAddr = '137.112.38.47'
PORT = 1874

HOST = ''

srcPort = 1125
dstPort = 105
commID = 312

rhp = RHP(dstPort, srcPort)
rhmp = RHMP(commID)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
    
    if data['type'] == '00':
        prettyPrintRHMP(rhmp.decode(data['payload']))
    
def prettyPrintRHMP(data):
    print(
'''-----
RHMP message
    type:    %s
    commID:  %s
    length:  %s
    payload: %s
-----''' % (data['type'], data['commID'], data['length'], data['payload']))

def test():
    
    print('starting')
    try:
        sock.bind((HOST, 1887))
        print('socket bound')
    except:
        print('failed')
        raise
    
    #message = rhp.sendCAM('hello')
    message = rhp.sendRHMP(rhmp.sendMessage_Request())
    
    print('Message before decoding: %s' % message)
    prettyPrintRHP(rhp.decode(message))
    #prettyPrintRHMP(rhmp.decode(rhp.decode(message)['payload']))
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
    
def run():
    print('Starting')
    try:
        sock.bind((HOST, 1887))
        print('Socket Bound')
    except:
        print('failed')
        raise
    
    message1 = rhp.sendCAM('hello')
    message2 = rhp.sendRHMP(rhmp.sendID_Request())
    message3 = rhp.sendRHMP(rhmp.sendMessage_Request())
    
    print('Sending First Message: ')
    prettyPrintRHP(rhp.decode(message1))
    
    received = False
    while not received:
        try:
            sock.sendto(bytes.fromhex(message1), (IPAddr, PORT))
            print('Message1 sent')
        except:
            print('failed to send message')
            raise
        
        try:
            data, addr = sock.recvfrom(1024)
            decoded = rhp.decode(data.hex())
            print('Message 1 received.')
            prettyPrintRHP(decoded)
            print('Response: ')
            print(''.join([chr(int(x,16)) for x in re.findall('..', decoded['payload'])]))
            received = True
        except AssertionError:
            print('Failed checksum, trying again in a moment.')
            sleep(2)
            
    print('\n----------------------------------\n')
    print('Sending Second Message:')
    prettyPrintRHP(rhp.decode(message2))
    
    received = False
    while not received:
        try:
            sock.sendto(bytes.fromhex(message2), (IPAddr, PORT))
            print('Message2 sent')
        except:
            print('failed to send message')
            raise
        
        try:
            data, addr = sock.recvfrom(1024)
            decoded = rhp.decode(data.hex())
            print('Message 2 received')
            prettyPrintRHP(decoded)
            RHMPpayload = rhmp.decode(decoded['payload'])['payload']
            print('Identifier: %d' % int(RHMPpayload,16))
            received = True
        except AssertionError:
            print('Failed checksum, trying again in a moment.')
            sleep(2)
            
    
    print('\n----------------------------------\n')
    print('Sending Third Message:')
    prettyPrintRHP(rhp.decode(message3))
    
    received = False
    while not received:
        try:
            sock.sendto(bytes.fromhex(message3), (IPAddr, PORT))
            print('Message3 sent')
        except:
            print('failed to send message')
            raise
        
        try:
            data, addr = sock.recvfrom(1024)
            decoded = rhp.decode(data.hex())
            print('Message 3 received')
            prettyPrintRHP(decoded)
            RHMPpayload = rhmp.decode(decoded['payload'])['payload']
            print('Response: ')
            print(''.join([chr(int(x,16)) for x in re.findall('..', RHMPpayload)]))
            received = True
        except AssertionError:
            print('Failed checksum, trying again in a moment.')
            sleep(2)
    
        

if __name__ == '__main__':
   run()