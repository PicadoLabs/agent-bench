import pytest
from serializer import TreeNode, TreeSerializer


def test_linear_tree_flattening():
    child2 = TreeNode("c2", "leaf2")
    child1 = TreeNode("c1", "leaf1", [child2])
    root = TreeNode("root", "top", [child1])

    flat = TreeSerializer.flatten_tree(root)
    assert len(flat) == 3
    assert flat[0]["id"] == "root"
    assert flat[0]["children_ids"] == ["c1"]
    assert flat[1]["id"] == "c1"
    assert flat[1]["children_ids"] == ["c2"]
    assert flat[2]["id"] == "c2"
    assert flat[2]["children_ids"] == []


def test_branching_tree_flattening():
    b1 = TreeNode("b1", 10)
    b2 = TreeNode("b2", 20)
    root = TreeNode("root", 0, [b1, b2])

    flat = TreeSerializer.flatten_tree(root)
    assert len(flat) == 3
    ids = [n["id"] for n in flat]
    assert ids == ["root", "b1", "b2"]


def test_cycle_detection_raises():
    node1 = TreeNode("n1", "val1")
    node2 = TreeNode("n2", "val2")
    node1.children.append(node2)
    # Create cycle: n2 -> n1
    node2.children.append(node1)

    with pytest.raises(ValueError, match="Cycle detected"):
        TreeSerializer.flatten_tree(node1)
