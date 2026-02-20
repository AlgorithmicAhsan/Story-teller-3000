import json

EOS = "\u241E"
EOP = "\u241D"
EOT = "\u0003"
SPECIAL_TOKENS = [EOS, EOP, EOT]


def load_tokenizer(base_path="."):

    # Load ordered merges list
    with open(f"{base_path}/merges.json", "r", encoding="utf-8") as f:
        merges_raw = json.load(f)
        merges = [
            (int(new_id), tuple(pair))
            for new_id, pair in merges_raw
        ]

    with open(f"{base_path}/vocab.json", "r", encoding="utf-8") as f:
        char2id = json.load(f)

    with open(f"{base_path}/id2char.json", "r", encoding="utf-8") as f:
        id2char = {int(k): v for k, v in json.load(f).items()}

    return merges, char2id, id2char


class BPETokenizer:

    def __init__(self, merges, char2id, id2char):
        self.merges = merges
        self.char2id = char2id
        self.id2char = id2char
        self.merge_dict = {new_id: pair for new_id, pair in merges}

    # Oldest → Newest
    def encode(self, text):

        tokens = []

        for c in text:
            if c in self.char2id:
                tokens.append(self.char2id[c])
            else:
                tokens.append(self.char2id.get(" ", 0))

        for new_id, (a, b) in self.merges:

            new_tokens = []
            i = 0

            while i < len(tokens):
                if i + 1 < len(tokens) and tokens[i] == a and tokens[i+1] == b:
                    new_tokens.append(new_id)
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1

            tokens = new_tokens

        return tokens

    # Newest → Oldest (recursive expansion)
    def decode(self, tokens):

        def expand(t):
            if t in self.merge_dict:
                a, b = self.merge_dict[t]
                return expand(a) + expand(b)
            return self.id2char.get(t, "")

        return "".join(expand(t) for t in tokens)


def get_tokenizer(base_path="."):
    merges, char2id, id2char = load_tokenizer(base_path)
    return BPETokenizer(merges, char2id, id2char)

def reconvert_special_tokens(text):
    text = text.replace(EOS, "")
    text = text.replace(EOP, "\n\n")
    text = text.replace(EOT, "")
    return text