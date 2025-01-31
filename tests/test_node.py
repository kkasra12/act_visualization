import pytest
from node import Node, node_sum, filter_words, WordTransformer, node_sum_sent


def test_node_initialization():
    node = Node("root")
    assert node.data == "root"
    assert node.freq == 0
    assert node.next == {}
    assert node.father is None


def test_node_addition():
    root = Node("root")
    child = root + "child"
    assert child.data == "child"
    assert root.next["child"] is child
    assert child.father is root
    assert child.freq == 1

    # Adding the same child should increase frequency
    _ = root + "child"
    assert root.next["child"].freq == 2


def test_node_root_property():
    root = Node("root")
    child = root + "child"
    grandchild = child + "grandchild"
    assert grandchild.root == root


def test_node_depth_property():
    root = Node("root")
    child = root + "child"
    grandchild = child + "grandchild"
    assert root.depth == 0
    assert child.depth == 1
    assert grandchild.depth == 2


def test_node_string_representation():
    root = Node("root")
    assert str(root) == f"N{root.node_id}[root]"
    assert repr(root) == f"Node(data=root, father=None, freq=0)"


def test_node_print():
    root = Node("root")
    child1 = root + "child1"
    child2 = root + "child2"
    grandchild = child1 + "grandchild"

    output = root.print()
    assert "graph LR" in output
    assert f"N{root.node_id}[root] --1--> N{child1.node_id}[child1]" in output
    assert f"N{root.node_id}[root] --1--> N{child2.node_id}[child2]" in output
    assert f"N{child1.node_id}[child1] --1--> N{grandchild.node_id}[grandchild]" in output


def test_node_sum():
    root = Node("<s>")
    result = node_sum(["word1", "word2", "word3"], start_node=root)
    assert result.data == "word3"
    assert root.next["word1"].freq == 1
    assert root.next["word1"].next["word2"].freq == 1
    assert root.next["word1"].next["word2"].next["word3"].freq == 1


def test_filter_words():
    abandoned_words = {"example"}
    assert filter_words("hello", abandoned_words) is True
    assert filter_words("a", abandoned_words) is False
    assert filter_words("!", abandoned_words) is False
    assert filter_words("example", abandoned_words) is False


def test_node_sum_sent(mocker):
    mocker.patch("node.word_tokenize", return_value=["Hello", "world"])
    mocker.patch("node.WordTransformer.word_transformer", side_effect=lambda x: x.lower())

    root = Node("<s>")
    result = node_sum_sent("Hello world!", start_node=root)

    assert result.data == "world"
    assert root.next["hello"].freq == 1
    assert root.next["hello"].next["world"].freq == 1
