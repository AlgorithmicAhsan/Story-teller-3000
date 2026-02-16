import random
from collections import Counter

class TrigramLanguageModel:
    def __init__(self, vocab_size):
        self.unigrams = Counter()
        self.bigrams = Counter()
        self.trigrams = Counter()
        self.total_tokens = 0
        self.vocab_size = vocab_size

    def unigram_prob(self, w):
        return (self.unigrams[w] + 1) / (self.total_tokens + self.vocab_size)

    def bigram_prob(self, w1, w2):
        denom = self.unigrams[w1] + self.vocab_size
        return (self.bigrams[(w1, w2)] + 1) / denom

    def trigram_prob(self, w1, w2, w3):
        denom = self.bigrams[(w1, w2)] + self.vocab_size
        return (self.trigrams[(w1, w2, w3)] + 1) / denom

    def interpolated_prob(self, w1, w2, w3, l1, l2, l3):
        p1 = self.unigram_prob(w3)
        p2 = self.bigram_prob(w2, w3)
        p3 = self.trigram_prob(w1, w2, w3)
        return l1 * p1 + l2 * p2 + l3 * p3

    def generate(self, prefix_tokens, l1, l2, l3, eot_id):
        tokens = list(prefix_tokens)
        while len(tokens) < 2:
            tokens.insert(0, tokens[0] if tokens else 0)

        while True:
            w1, w2 = tokens[-2], tokens[-1]
            probs = [self.interpolated_prob(w1, w2, t, l1, l2, l3) for t in range(self.vocab_size)]
            next_token = random.choices(range(self.vocab_size), weights=probs, k=1)[0]
            tokens.append(next_token)
            if next_token == eot_id:
                break
        return tokens