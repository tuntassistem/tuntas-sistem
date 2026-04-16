# utils/quotes.py
import random

QUOTES_LIST = [
    '"In God we trust, all others must bring data." – W. Edwards Deming',
    '"Integrity is doing the right thing, even when no one is watching." – C.S. Lewis',
    '"Auditing is the art of verifying the truth without being an enemy of progress."',
    '"Tuntaskan hari ini, tanpa menyisakan beban untuk esok."',
    '"Trust, but verify." – Ronald Reagan',
    '"Kejujuran adalah bab pertama dalam buku kebijaksanaan." – Thomas Jefferson'
]

def get_random_quote():
    return random.choice(QUOTES_LIST)
