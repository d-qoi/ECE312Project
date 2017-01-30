'''
Created on Jan 24, 2017

@author: hirschag
'''


class RHP:
    '''
    Rose-Hulman Protocol
    
    Type[8] DestPort/length[16] SourcePort[16] Payload[%8] Buffer[8/0] Checksum[16]
    
    Types:
        1: Control Access Message
        0: RHMP Message
    '''


    def __init__(self, dstPort, srcPort):
        assert(0 < dstPort < 0x10000) # making sure it is not too long or negative
        assert(0 < srcPort < 0x10000)
        
        self.dstPort = '%04x'%dstPort # converting straight to hex
        self.srcPort = '%04x'%srcPort
        
    
    def computeChecksum(self, data):
        assert(len(data)%4 == 0)
        try:
            int(data,16)
        except ValueError:
            raise
        
        runningTotal = int(data[:4],16) 
        # assuming that we compute the checksum in order, rather than swapping the first and last two values ('abcd' -> 'cdab')
        data = data[4:]
        
        while data:
            runningTotal += int(data[:4],16)
            data = data[4:]
            
            runningTotal = runningTotal - 0xFFFF if runningTotal > 0xFFFF else runningTotal
        
        return hex(0XFFFF - runningTotal)[2:]
        
            
    def validateChecksum(self, data):
        return self.computeChecksum(data) == '0'
        
    
    def sendRHMP(self, payload):
        try:
            int(payload,16)
            assert(0 < len(payload)/2 < 0x10000) # less than 17 bits of data and not an empty string
        except ValueError:
            raise
        
        length = '%04x'%int(len(payload)/2) # 2 hex characters is one byte.
        
        cwns = '00' + length + self.srcPort + payload
        cwns += '00' if len(cwns)%4 == 2 else ''
                
        checksum = self.computeChecksum(cwns)
        
        return cwns + checksum
    
    
    def sendCAM(self, payload):
        '''
        The payload here is an ascii string, this will convert it.
        '''
        
        payload = ''.join([hex(ord(c))[2:] for c in list(payload)])
        
        cwns = '01' + self.dstPort + self.srcPort + payload
        cwns += '00' if len(cwns)%4 == 2 else ''
        
        checksum = self.computeChecksum(cwns)
        
        return cwns + checksum
    
    def decode(self, data):
        assert(self.validateChecksum(data))
        
        decoded = dict()
        decoded['type'] = data[:2]
        
        if decoded['type'] == '00':
            decoded['length'] = data[2:6]
            decoded['dstPort'] = '-1'
        elif decoded['type'] == '01':
            decoded['length'] = '-1'
            decoded['dstPort'] = int(data[2:6],16)
        else:
            return "UnknownType"
        
        
        decoded['srcPort'] = int(data[6:10],16)
        decoded['checksum'] = data[-4:]
        decoded['payload'] = data[10:-4] if len(data)%4 == 0 else data[10:-6]
        
        
        return decoded
        
class RHMP:
    '''
    Rose-Hulman Message Protocol
    
    Type[6], CommID [10], length[8], Payload[%8]
    '''
    
    def __init__(self, commID):
        '''
        commID is currently passed as an Integersubt
        This may need to change later, or if it is easier
        '''
        assert(commID < 0x400) # 0x400 == 0b0100 0000 0000
        
        self.commID = commID
        
    def sendReserved(self):
        head = (0<<10) + self.commID
        cwns = '%04x'%(head)
        cwns += '00'
        return cwns
    
    def sendID_Request(self):
        head = self.commID + (1<<10)
        cwns = '%04x'%(head)
        cwns += '00'
        return cwns
    
    def sendID_Response(self, ID):
        '''
        This will take an integer, not a hex value, remember this
        '''
        assert(isinstance(ID, int))
        assert(ID <= (1<<32)-1)
        
        head = (4<<10) + self.commID
        cwns = '%04x'%(head) # length is 4 bytes
        cwns += '04' + '%04x'%(ID)
        return cwns
    
    def sendMessage_Request(self):
        head = (8<<10) + self.commID
        cwns = '%04x'%(head)
        cwns += '00'
        return cwns
    
    def sendMessage_Response(self, message):
        head = (16<<10) + self.commID
        cwns = '%04x'%(head)
        
        payload = ''.join([hex(ord(c))[2:] for c in list(message)])
        
        length = '%02x' % int(len(payload)/2)
        assert(len(length) <= 2) # is string length
        
        return cwns + length + payload
    
    def decode(self, data):
        decoded = dict()
        head = int(data[:4],16)
        decoded['type'] = head>>10
        decoded['commID'] = head & 0b1111111111
        decoded['length'] = data[4:6]
        decoded['payload'] = data[6:]
        
        return decoded
            
    
        
    
        
    
        
        