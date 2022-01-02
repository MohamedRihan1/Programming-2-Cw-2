#import datetime
import time
from hashlib import *
import cryptography
import json
import requests
from urllib.parse import urlparse



class Block:
    blockindex = 0
    def __init__(self,data,sender,receiver,file_key,prevhash='0'):
        self.index=Block.blockindex
        Block.blockindex+=1
        self.timestamps = time.localtime()
        self.data=data
        self.nonce=0
        self.sender=sender
        self.receiver=receiver
        self.prevhash=prevhash
        self.file_key=file_key
        self.hash=self.proof_of_work()

    def hash_calculate(self):
        return sha256((str(str(self.data)+str(self.sender)+str(self.receiver)+str(self.nonce)+str(self.timestamps)+self.prevhash)).encode('utf-8')).hexdigest()

    def blockData(self,key):
        ts=str(time.strftime("%d %B %Y , %I:%M:%S %p",  self.timestamps))
        block_dict ={"index":self.index,"ts":ts,"Proof":self.nonce,"prev_hash":self.prevhash,"Sender":self.sender,"Receiver":self.receiver,"file":self.data,"key":self.file_key}
        return block_dict[key]
        
    def proof_of_work(self,difficulty=4):
        self.nonce=0
        while(self.hash_calculate()[:difficulty]!='0'*difficulty):
            self.nonce+=1
        return self.hash_calculate()
        
# Building a Blockchain

class Blockchain:

    def __init__(self):
        self.chain = []
        self.create_genesis()
        self.nodes = set()
        self.nodes.add("127.0.0.1:5111")


    def create_genesis(self):
        genesis=Block(data= 'N.A',sender= 'N.A',receiver= 'N.A',file_key='0',prevhash='0')
        self.chain.append(genesis)
        
    def create_block(self,data,sender,receiver,file_key,prevhash):
        new_block=Block(data,sender,receiver,file_key,prevhash)
        self.chain.append(new_block)
        return new_block
   
    def get_previous_block(self):
        return self.chain[-1]

    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block.prevhash != previous_block.hash:
                return False

            if block[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_file(self, sender, receiver, data,file_key):
        previous_block = self.get_previous_block()
        prevhash = previous_block.hash
        self.create_block( data, sender, receiver,file_key, prevhash)
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False