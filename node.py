from functools import lru_cache
from nltk.tokenize import word_tokenize  # type: ignore
from nltk.corpus import stopwords  # type: ignore
from nltk.stem import WordNetLemmatizer  # type: ignore
from typing import Optional
from string import punctuation

stop_words = set(stopwords.words("english"))
punctuation_set = set(punctuation)


class Node:
    next: dict[str, "Node"]
    data: str

    node_id = 0

    def __init__(self, data):
        self.data = data
        self.father = None
        self.freq = 0
        self.next = {}
        self.node_id = Node.node_id
        Node.node_id += 1

    @property
    def root(self) -> "Node":
        if self.father is None:
            return self
        else:
            return self.father.root

    @property
    def depth(self) -> int:
        if self.father is None:
            return 0
        else:
            return self.father.depth + 1

    def __str__(self) -> str:
        return f"N{self.node_id}[{self.data}]"

    def __repr__(self) -> str:
        return f"Node(data={self.data}, father={self.father}, freq={self.freq})"

    def __getitem__(self, key: str) -> "Node":
        return self.next[key]

    def __add__(self, other: "str | Node") -> "Node":
        if isinstance(other, str):
            other = Node(other)
        elif not isinstance(other, Node):
            raise TypeError(f"Expected Node, got {type(other)}")
        if other.data not in self.next:
            self.next[other.data] = other
            other.father = self
        self.next[other.data].freq += 1
        return self.next[other.data]

    def __radd__(self, other: int) -> "Node":
        if other == 0:
            return self
        else:
            raise TypeError(f"Expected int, got {type(other)}")

    def _print(self, min_freq: int, max_depth: int | float) -> list[str]:
        ans = []
        for key, val in self.next.items():
            if val.freq < min_freq:
                continue
            ans.append(f"{self} --{val.freq}--> {val}")
            if val.depth < max_depth:
                ans.extend(val._print(min_freq=min_freq, max_depth=max_depth - 1))
        return ans

    def print(self, min_freq=1, max_depth=-1) -> str:
        """
        Print the graph in mermaid format

        Args:
            min_freq (int, optional): Minimum frequency to print. The ndoes wich `node.freq < min_freq will` not be printed Defaults to 1.
            max_depth (int, optional): Maximum depth to print. Defaults to -1 means all the tree.
        Returns:
            str: The graph in mermaid format
        """
        if max_depth == -1:
            max_depth = float("inf")
        return "\n".join(
            ["```mermaid", "graph LR"]
            + self._print(min_freq=min_freq, max_depth=max_depth)
            + ["```"]
        )


def node_sum(vals: list[Node | str], start_node=None) -> Node:
    if start_node is None:
        start_node = Node("<s>")
    ans = start_node
    for val in vals:
        ans += val
    return ans


def filter_words(word: str, abandoned_words: set) -> bool:
    return (
        word != ""
        and word not in punctuation_set
        and word not in stop_words
        and len(word) > 2
        and word not in abandoned_words
        and word.isalpha()
    )


class WordTransformer:
    wn = WordNetLemmatizer()

    @classmethod
    @lru_cache
    def word_transformer(cls, word: str) -> str:
        return cls.wn.lemmatize(word.lower().strip())


def node_sum_sent(sent: str, start_node=None, abandoned_words: set[str] = None) -> Node:  # type: ignore
    if abandoned_words is None:
        abandoned_words = set()

    return node_sum(
        [
            WordTransformer.word_transformer(word)
            for word in word_tokenize(sent)
            if filter_words(word.lower().strip(), abandoned_words)
        ],
        start_node=start_node,
    )


if __name__ == "__main__":
    start_node = Node("<s>")
    a = start_node + "b"
    b = start_node + "c"
    _ = start_node + "b"
    _ = start_node + "c"
    print(a)
    print(b)
    print(node_sum(["a", "b", "c"], start_node=start_node))
    print(start_node["b"].freq)
    print(start_node["c"].freq)
    print(start_node.next)
    print(start_node.print())
