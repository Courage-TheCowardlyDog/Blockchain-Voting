from block import Block
from vote import Vote
from hashlib import sha256

class Blockchain(object):
    difficulty = 2
    status = 0
    def __init__(self,candidates_list):
        self.chain = []
        self.unconfirmed_votes = []
        self.candidates = candidates_list
        self.create_genesis_block()

    def previous_block(self):
        return self.chain[-1]

    def create_genesis_block(self):
        negative_hash = sha256("This is the genesis Block.".encode()).hexdigest()
        #For first block, we enter candidates to determine the order of votes
        block_zero = Block(0, negative_hash, self.candidates)
        #Hash calculated to ensure correct nonce for genesis block
        hash0 = self.proof_of_work(block_zero) 
        self.chain.append(block_zero)

    def new_block(self, previous_hash_inp):
        """
        Create and Add new block to the blockchain upon verifying:
        1) The block has a valid Hash
        2) The previous index block's hash is a match to the hash referred
        in this block.
        """
        block = Block(index=len(self.chain),
                      previous_hash=previous_hash_inp,
                      transactions=self.unconfirmed_votes)
        previous_hash_from_chain = self.previous_block().get_block_hash()
        block_hash = self.proof_of_work(block)

        if Blockchain.status == 0:
            return False
        if previous_hash_inp != previous_hash_from_chain:
            return False
        if not Blockchain.check_hash_validity(block, block_hash):
            return False

        self.chain.append(block) #Add Block to the Chain
        self.unconfirmed_votes = [] #reset the transaction list
        return True
    
    def proof_of_work(self, block:Block):
        """
        Function to change nonce until we get a hash that is of
        acceptable criteria for the blockchain.
        """
        block.nonce = 0
        computed_hash = block.get_block_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.get_block_hash()
        return computed_hash
    
    @classmethod        
    def check_hash_validity(cls, block, hash):
        return (hash.startswith('0'*Blockchain.difficulty) and 
              hash == block.get_block_hash())

    def create_new_transaction(self, vote):
      new_vote = Vote(vote)
      if Blockchain.status == 0:
          print("Elections Stopped. Unable to register your Vote.")
          return False
      self.unconfirmed_votes.append(new_vote)
    
    def display_results(self):
        length = len(self.candidates)
        summed_votes = [0 for i in range(length)]
        if Blockchain.status == 1:
            return "The Voting phase is still on"
        for block in self.chain:
            if block == self.chain[0]:
                continue
            elif block == self.chain[-1]:
                for vote in block.transactions:
                    if not isinstance(vote, Vote):
                        continue
                    vote_list = list(vote.vote)
                    for i in range(len(vote_list)):
                        summed_votes[i]+=int(vote_list[i])
            else:
                for vote in block.transactions:
                    vote_list = list(vote.vote)
                    for i in range(len(vote_list)):
                        summed_votes[i]+=int(vote_list[i])
        
        return summed_votes
