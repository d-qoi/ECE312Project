'''
Created on Jan 24, 2017

@author: hirschag
'''
from reportlab.lib.pagesizes import B1

def flipBits(string):
    assert(len(string) == 4)
    return string[-2:] + string[:-2]

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
        
        self.dstPort = flipBits('%04x'%(dstPort)) # converting straight to hex
        self.srcPort = flipBits('%04x'%(srcPort))
        
        
    
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
        #data = data[:-4] + flipBits(data[-4:])
        return self.computeChecksum(data) == '0'
        
        
    def sendRHMP(self, payload):
        try:
            int(payload,16)
            assert(0 < len(payload)/2 < 0x10000) # less than 17 bits of data and not an empty string
        except ValueError:
            raise
        
        
        cwns = '00' + self.dstPort + self.srcPort + payload
        cwns += '00' if len(cwns)%4 == 2 else ''
                
        checksum = (self.computeChecksum(cwns))
        
        return cwns + checksum
    
    
    def sendCAM(self, payload):
        '''
        The payload here is an ascii string, this will convert it.
        '''
        
        payload = ''.join([hex(ord(c))[2:] for c in list(payload)])
        
        length = flipBits('%04x'%int(len(payload)/2)) # 2 hex characters is one byte.
        
        cwns = '01' + length + self.srcPort + payload
        cwns += '00' if len(cwns)%4 == 2 else ''
        
        checksum = (self.computeChecksum(cwns))
        
        return cwns + checksum
    
    def decode(self, data):
        assert(self.validateChecksum(data))
        
        decoded = dict()
        decoded['type'] = data[:2]
        
        if decoded['type'] == '01':
            decoded['length'] = flipBits(data[2:6])
            decoded['dstPort'] = '-1'
        elif decoded['type'] == '00':
            decoded['length'] = '-1'
            decoded['dstPort'] = int(flipBits(data[2:6]),16)
        else:
            return "UnknownType"
        
        
        decoded['srcPort'] = int(flipBits(data[6:10]),16)
        decoded['checksum'] = data[-4:]
        decoded['payload'] = data[10:-4]
        
        
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
        
    def modifyHead(self, head):
        assert(len(head) == 4)
        head = int(head,16)
        b10 = head & 0b11
        rest = head >> 2
        head = (b10 << 14) + rest
        return '%04x'%head
    
    def unmodifyHead(self, head):
        assert(len(head) == 4)
        head = int(head,16)
        b10 = head >> 14
        rest = head << 2
        head = b10 + rest
        return '%04x'%head
        
    def sendReserved(self):
        head = (1<<10) + self.commID
        cwns = self.modifyHead('%04x'%(head))
        cwns += '00'
        return cwns
    
    def sendID_Request(self):
        head = self.commID + (2<<10)
        cwns = self.modifyHead('%04x'%(head))
        cwns += '00'
        return cwns
    
    def sendID_Response(self, ID):
        '''
        This will take an integer, not a hex value, remember this
        '''
        assert(isinstance(ID, int))
        assert(ID <= (1<<32)-1)
        
        head = (4<<10) + self.commID
        cwns = self.modifyHead('%04x'%(head)) # length is 4 bytes
        cwns += '04' + '%04x'%(ID)
        return cwns
    
    def sendMessage_Request(self):
        head = (8<<10) + self.commID
        cwns = self.modifyHead('%04x'%(head))
        cwns += '00'
        return cwns
    
    def sendMessage_Response(self, message):
        head = (16<<10) + self.commID
        cwns = self.modifyHead('%04x'%(head))
        
        payload = ''.join([hex(ord(c))[2:] for c in list(message)])
        
        length = '%02x' % int(len(payload)/2)
        assert(len(length) <= 2) # is string length
        
        return cwns + length + payload
    
    def decode(self, data):
        decoded = dict()
        head = int(self.unmodifyHead(data[:4]),16)
        decoded['type'] = head>>10
        decoded['commID'] = head & 0b1111111111
        decoded['length'] = data[4:6]
        decoded['payload'] = data[6:]
        
        return decoded
            
    
        
    
        
    
        
        