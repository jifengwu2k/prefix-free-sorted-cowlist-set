# `prefix-free-sorted-cowlist-set`

A Python implementation of a prefix-free, sorted set of [COWList](https://pypi.org/project/cowlist/), backed by a trie
data structure for efficient prefix checking and maintenance of sorted order.

## Features

- **Prefix-Free Guarantee**: Ensures no sequence in the set is a prefix of any other sequence
- **Sorted Order**: Maintains all COWList in lexicographical order
- **Efficient Operations**:
    - O(k) time complexity for add/discard operations (where k is sequence length)
    - Fast prefix checking via trie traversal
- **Memory Efficient**: Uses Copy-On-Write semantics for list storage
- **Pythonic Interface**: Implements both `MutableSet` and `Sequence` protocols

## Installation

```bash
pip install prefix-free-sorted-cowlist-set
```

## Usage

```python
# coding=utf-8
from prefix_free_sorted_cowlist_set import PrefixFreeSortedCOWListSet
from cowlist import COWList

# Create a new set
pf_set = PrefixFreeSortedCOWListSet()

# Add sequences (returns True if successful)
assert pf_set.add(COWList([1, 2, 3]))  # True
assert pf_set.add(COWList([1, 2, 4]))  # True
assert pf_set.add(COWList([1, 3]))  # True

# Try to add a prefix (will fail)
assert not pf_set.add(COWList([1, 2]))  # False - violates prefix-free property

# Check membership
assert COWList([1, 2, 3]) in pf_set  # True

# Iterate in sorted order
assert list(pf_set) == [COWList([1, 2, 3]), COWList([1, 2, 4]), COWList([1, 3])]

# Reverse iteration
assert list(reversed(pf_set)) == [COWList([1, 3]), COWList([1, 2, 4]), COWList([1, 2, 3])]

# Remove sequences
assert pf_set.discard(COWList([1, 2, 3]))
assert list(pf_set) == [COWList([1, 2, 4]), COWList([1, 3])]

# Length of set
assert len(pf_set) == 2

# Index access (sorted order)
assert pf_set[-1] == COWList([1, 3])
```

## Use Cases

### File System Paths

```python
from prefix_free_sorted_cowlist_set import PrefixFreeSortedCOWListSet
from cowlist import COWList

# Store unique file paths where no path is a prefix of another
paths = PrefixFreeSortedCOWListSet()
paths.add(COWList(["usr", "local", "bin"]))
paths.add(COWList(["usr", "local", "lib"]))
# paths.add(COWList(["usr", "local"]))  # This would fail - prefix violation
```

### Domain Names

```python
from prefix_free_sorted_cowlist_set import PrefixFreeSortedCOWListSet
from cowlist import COWList

# Store domain names ensuring no subdomain conflicts
domains = PrefixFreeSortedCOWListSet()
domains.add(COWList(["example", "com"]))
domains.add(COWList(["sub", "example", "com"]))
# domains.add(COWList(["example"]))  # This would fail
```

### Routing Tables

```python
from prefix_free_sorted_cowlist_set import PrefixFreeSortedCOWListSet
from cowlist import COWList

# Network routing paths where no route should be a prefix of another
routes = PrefixFreeSortedCOWListSet()
routes.add(COWList([192, 168, 1, 0]))
routes.add(COWList([192, 168, 2, 0]))
```

## API Reference

### PrefixFreeSortedCOWListSet

#### Methods

- `add(cowlist: COWList[T]) -> bool`: Add a COWList to the set if it doesn't violate the prefix-free property
- `discard(cowlist: COWList[T]) -> bool`: Remove a COWList from the set if present
- `__contains__(item: COWList[T]) -> bool`: Check if a COWList is in the set
- `__getitem__(index: int) -> COWList[T]`: Get COWList at specified index (sorted order)
- `__iter__() -> Iterator[COWList[T]]`: Iterate over COWList in sorted order
- `__len__() -> int`: Get number of COWList objects in the set
- `__reversed__() -> Iterator[COWList[T]]`: Iterate in reverse sorted order

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).