import hashlib
from sortedcontainers import SortedDict

class ConsistentHashRing:
    def __init__(self, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring = SortedDict()
        self.nodes = set()

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node: str):
        self.nodes.add(node)
        for i in range(self.virtual_nodes):
            vnode_key = f"{node}#vnode{i}"
            ring_hash = self._hash(vnode_key)
            self.ring[ring_hash] = node
        print(f"[Ring] Added node: {node} ({self.virtual_nodes} vnodes)")

    def remove_node(self, node: str):
        self.nodes.discard(node)
        for i in range(self.virtual_nodes):
            vnode_key = f"{node}#vnode{i}"
            ring_hash = self._hash(vnode_key)
            self.ring.pop(ring_hash, None)
        print(f"[Ring] Removed node: {node}")

    def get_node(self, key: str) -> str:
        if not self.ring:
            raise Exception("No nodes in ring")
        key_hash = self._hash(key)
        keys = self.ring.keys()
        # Find first node clockwise from key_hash
        idx = self.ring.bisect_left(key_hash)
        if idx == len(keys):
            idx = 0
        return self.ring[keys[idx]]

    def get_distribution(self) -> dict:
        counts = {node: 0 for node in self.nodes}
        for node in self.ring.values():
            counts[node] += 1
        return counts

# Global ring instance
ring = ConsistentHashRing(virtual_nodes=150)

def init_ring():
    ring.add_node("instance-1")
    ring.add_node("instance-2")
    ring.add_node("instance-3")
    print("[Ring] Consistent hash ring initialized with 3 nodes")