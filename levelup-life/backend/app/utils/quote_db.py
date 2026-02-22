import random
from typing import Optional

QUOTES = {
    "fitness": [
        {"text": "The body achieves what the mind believes.", "author": "Unknown"},
        {"text": "Push harder than yesterday if you want a different tomorrow.", "author": "Unknown"},
        {"text": "No pain, no gain. Shut up and train.", "author": "Unknown"},
    ],
    "productivity": [
        {"text": "Focus on being productive instead of busy.", "author": "Tim Ferriss"},
        {"text": "The secret of getting ahead is getting started.", "author": "Mark Twain"},
        {"text": "Done is better than perfect.", "author": "Sheryl Sandberg"},
    ],
    "learning": [
        {"text": "Live as if you were to die tomorrow. Learn as if you were to live forever.", "author": "Gandhi"},
        {"text": "The more that you read, the more things you will know.", "author": "Dr. Seuss"},
        {"text": "An investment in knowledge pays the best interest.", "author": "Benjamin Franklin"},
    ],
    "general": [
        {"text": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
        {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
        {"text": "Start where you are. Use what you have. Do what you can.", "author": "Arthur Ashe"},
    ],
}


def select_quote(domain: Optional[str] = None) -> dict:
    pool = QUOTES.get(domain, []) + QUOTES["general"]
    return random.choice(pool)
