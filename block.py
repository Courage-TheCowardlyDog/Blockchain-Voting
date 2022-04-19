from hashlib import sha256
from datetime import datetime

class Block(object):
    def __init__(self, index, previous_hash, transactions, nonce=0):
        self.index = index
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = datetime.now()

    def __repr__(self):
        return "<Block index: %s  Nonce: %s  Transactions: %s  Timestamp: %s  Previous_hash: %s>" % (self.index, self.nonce, self.transactions, self.timestamp, self.previous_hash)

    def get_block_hash(self):
        block_string = "{}{}{}{}{}".format(self.index,self.nonce,self.previous_hash,self.transactions, self.timestamp)
        block_hash = sha256(block_string.encode())
        return block_hash.hexdigest()
        