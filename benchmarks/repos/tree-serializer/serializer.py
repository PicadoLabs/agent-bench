# serializer.py - Recursive Tree Node Serializer & Flattener
from typing import Dict, Any, List, Optional, Set


class TreeNode:
    def __init__(self, id: str, value: Any, children: Optional[List["TreeNode"]] = None):
        self.id = id
        self.value = value
        self.children = children if children is not None else []


class TreeSerializer:
    @staticmethod
    def flatten_tree(root: TreeNode) -> List[Dict[str, Any]]:
        """
        Flatten a hierarchical TreeNode structure into a flat list of node dicts:
        - Format: {"id": node.id, "value": node.value, "children_ids": [c.id for c in node.children]}
        - Must detect circular references (cycles) and raise ValueError("Cycle detected in tree")
        - Must maintain breadth-first or depth-first unique visitation without duplicates.
        """
        visited: Set[str] = set()
        result: List[Dict[str, Any]] = []

        def traverse(node: TreeNode, path: Set[str]):
            # BUG: Path cycle detection check is missing!
            # BUG: visited deduplication is missing, causing infinite loop on cycles or repeated nodes
            item = {
                "id": node.id,
                "value": node.value,
                "children_ids": [c.id for c in node.children]
            }
            result.append(item)
            for child in node.children:
                traverse(child, path)

        traverse(root, set())
        return result
