import time
from datetime import timedelta, datetime


BYTE_IN_BITS = 256
HEX_BASE_TO_NUMBER = 16
SECONDS_TO_EXPIRE = 20


GENESIS_BLOCK = Block(
    version=1,
    timestamp=1231476865,
    difficulty=1,
    nonce=1,
    previous_hash="000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f",
    transactions=(Transaction("Satoshi Nakamoto", "Satoshi Nakamoto", 50),)
)


def calculate_difficulty_target(difficulty_bits: int) -> int:
    return 2 ** (BYTE_IN_BITS - difficulty_bits)


class Blockchain:
    VERSION = 1
    DIFFICULTY = 10
    MINUTES_TOLERANCE = 1

    def __init__(self):
        self.chain = [GENESIS_BLOCK]

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def get_difficulty(self) -> int:
        return self.DIFFICULTY

    def add_block(self, block: Block) -> bool:
        is_valid = self._validate_block(block)
        if is_valid:
            self.chain.append(block)

        return is_valid

    def _validate_block(self, candidate: Block) -> bool:
        if candidate.version != self.VERSION:
            return False

        last_block = self.get_last_block()
        if candidate.previous_hash != encode_block(last_block):
            return False
        
        if candidate.difficulty != self.DIFFICULTY:
            return False

        min_allowed_time = (datetime.now() - timedelta(minutes=self.MINUTES_TOLERANCE)).timestamp()
        if candidate.timestamp < min_allowed_time:
            return False

        candidate_hash = encode_block(candidate)
        candidate_decimal = int(candidate_hash, HEX_BASE_TO_NUMBER)

        target = calculate_difficulty_target(self.DIFFICULTY)
        is_block_valid = candidate_decimal < target

        return is_block_valid


blockchain = Blockchain()


def mine_proof_of_work(nonce: int, difficulty: int, prev_hash: str) -> tuple[bool, Block]:
    block = create_block(nonce, difficulty, prev_hash)
    encoded_block = encode_block(block)
    block_encoded_as_number = int(encoded_block, HEX_BASE_TO_NUMBER)
    decimal_target = calculate_difficulty_target(difficulty)

    if block_encoded_as_number < decimal_target:
        return True, block

    return False, block


nonce = 0
start_time = time.time()
found = False
prev_hash = encode_block(blockchain.get_last_block())

while not found:
    found, block = mine_proof_of_work(nonce, blockchain.get_difficulty(), prev_hash)

    if found:
        blockchain.add_block(block)
    else:
        print(f"❌ Nonce {nonce} didn't meet the difficulty target...")
        nonce += 1

    end_time = time.time()
    elapsed_time = end_time - start_time

    if elapsed_time > SECONDS_TO_EXPIRE:
        raise TimeoutError(
            f"Couldn't find a block with difficulty {blockchain.get_difficulty()} fast enough"
        )

print(
    f"✅ Nonce {nonce} meet difficulty target, you mined the block in {timedelta(seconds=elapsed_time)}!"
)
print("Here's the the blockchain: ⛓️")
print(blockchain.chain)