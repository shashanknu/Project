import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.blockchain_file = 'blockchain.json'
        self.load_chain()

    # Load the blockchain from a file (if it exists)
    def load_chain(self):
        try:
            with open(self.blockchain_file, 'r') as f:
                self.chain = json.load(f)
        except FileNotFoundError:
            self.create_genesis_block()

    # Save the blockchain to a file
    def save_chain(self):
        with open(self.blockchain_file, 'w') as f:
            json.dump(self.chain, f, indent=4)

    # Create the initial genesis block
    def create_genesis_block(self):
        genesis_block = {
            'index': 0,
            'timestamp': time(),
            'data': 'Genesis Block',
            'previous_hash': '0',
            'hash': self.hash_block({
                'index': 0,
                'timestamp': time(),
                'data': 'Genesis Block',
                'previous_hash': '0'
            })
        }
        self.chain.append(genesis_block)
        self.save_chain()

    # Add a new block with IPFS hash data
    def add_block(self, ipfs_hash):
        last_block = self.chain[-1]
        new_block = {
            'index': len(self.chain),
            'timestamp': time(),
            'data': ipfs_hash,
            'previous_hash': last_block['hash'],
            'hash': self.hash_block({
                'index': len(self.chain),
                'timestamp': time(),
                'data': ipfs_hash,
                'previous_hash': last_block['hash']
            })
        }
        self.chain.append(new_block)
        self.save_chain()
        return new_block

    # Hash a block
    @staticmethod
    def hash_block(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # Retrieve the blockchain
    def get_chain(self):
        return self.chain

    # Verify the integrity of a file by checking its IPFS hash in the blockchain
    def verify_file(self, ipfs_hash):
        for block in self.chain:
            if block['data'] == ipfs_hash:
                return block  # Return the block containing the IPFS hash
        return None
