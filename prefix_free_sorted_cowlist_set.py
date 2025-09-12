# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from typing import Generic, Iterable, MutableMapping, Optional, Sequence, TypeVar, MutableSet

from cowlist import COWList
from put_back_iterator import PutBackIterator
from sortedcontainers import SortedDict, SortedSet

T = TypeVar('T')


class PrefixFreeSortedTrieNode(Generic[T]):
    __slots__ = ('children', 'is_terminal')

    def __init__(self):
        self.children = SortedDict()  # type: MutableMapping[T, PrefixFreeSortedTrieNode[T]]
        self.is_terminal = False  # type: bool


def add(prefix_free_sorted_trie_node, sequence_put_back_iterator):
    # type: (PrefixFreeSortedTrieNode[T], PutBackIterator[T]) -> Optional[PrefixFreeSortedTrieNode[T]]
    """
    Attempts to add a new sequence to a prefix-free sorted trie.

    This function ensures that the prefix-free property is maintained:
    - It does NOT allow insertion if the sequence to add is a prefix of any existing sequence,
      or if any existing sequence is a prefix of the sequence to add.
    - The trie is mutated only if the sequence can be safely added without violation of the
      prefix-free property; otherwise, the trie remains unchanged.

    Args:
        prefix_free_sorted_trie_node (PrefixFreeSortedTrieNode[T]):
            The root node of the trie subtree to which the sequence should be added.
        sequence_put_back_iterator (PutBackIterator[T]):
            A PutBackIterator over the sequence to insert.

    Returns:
        Optional[PrefixFreeSortedTrieNode[T]]:
            The terminal node corresponding to the added sequence if insertion succeeded,
            or None if the sequence could not be added without violating the prefix-free constraint.
    """
    # Is the current node the end of another sequence?
    # This is NOT allowed, as there exists an existing prefix of our sequence to add
    if prefix_free_sorted_trie_node.is_terminal:
        return None

    else:
        # Do we have any more elements to add?
        if sequence_put_back_iterator.has_next():
            # Retrieve the next element
            # This advances the iterator
            next_element = next(sequence_put_back_iterator)

            # Does the current node have that element associated with a child?
            if next_element in prefix_free_sorted_trie_node.children:
                # In that case, try adding the remaining sequence to that child.
                child = prefix_free_sorted_trie_node.children[next_element]
                recursive_call_result = add(child, sequence_put_back_iterator)

                # Successful = we have obtained the (already mutated) last node of our sequence
                if recursive_call_result is not None:
                    return recursive_call_result

                # Failure = we have obtained None, and no nodes have been mutated
                else:
                    return None
            else:
                # We create a temporary child and operate on that
                child = PrefixFreeSortedTrieNode()
                recursive_call_result = add(child, sequence_put_back_iterator)

                # Successful = we have obtained the (already mutated) last node of our sequence
                # In that case, add the temporary child to our current node.
                if recursive_call_result is not None:
                    prefix_free_sorted_trie_node.children[next_element] = child
                    return recursive_call_result

                # Failure = we have obtained None, and no nodes have been mutated
                # Let the temporary child be garbage-collected, and we won't modify the current node either.
                else:
                    return None

        # We don't have any more elements to add
        else:
            # But does the current node have children?
            # In that case, we are the prefix of another sequence
            # This is NOT allowed
            if prefix_free_sorted_trie_node.children:
                return None
            # Otherwise, mark the current node as the end of our sequence
            else:
                prefix_free_sorted_trie_node.is_terminal = True
                return prefix_free_sorted_trie_node


def discard(sorted_trie_node, sequence_put_back_iterator):
    # type: (PrefixFreeSortedTrieNode[T], PutBackIterator[T]) -> bool
    """
    Attempts to remove a sequence from the prefix-free sorted trie.

    Args:
        sorted_trie_node (PrefixFreeSortedTrieNode[T]):
            The root/subroot of the trie.
        sequence_put_back_iterator (PutBackIterator[T]):
            PutBackIterator over the sequence to remove.

    Returns:
        bool: True if removed, False if not found.
    """
    # Are there more elements?
    if sequence_put_back_iterator.has_next():
        next_element = next(sequence_put_back_iterator)

        if next_element in sorted_trie_node.children:
            child = sorted_trie_node.children[next_element]
            did_remove = discard(child, sequence_put_back_iterator)

            if did_remove:
                # After deletion, check if child is now unnecessary and prune it.
                if not child.children and not child.is_terminal:
                    del sorted_trie_node.children[next_element]

                return True
            else:
                return False
        else:
            return False
    # No more elements.
    # This node should be a terminal node to delete.
    else:
        if sorted_trie_node.is_terminal:
            sorted_trie_node.is_terminal = False
            return True
        else:
            return False


class PrefixFreeSortedCOWListSet(MutableSet[COWList[T]], Sequence[COWList[T]]):
    """
    A prefix-free, sorted set of COWList.

    This data structure acts as a set of COWList augmented with the following properties:
    - **Prefix-free:** No COWList in the set is a prefix of another COWList. Attempts
      to add a COWList that is a prefix of, or is prefixed by, an existing COWList are rejected.
    - **Sorted:** All contained COWList are maintained in sorted order,
      according to their natural (lexicographical) ordering.
    - **Efficient prefix checking:** Backed by a trie for efficient enforcement of the prefix-free property.

    This collection is useful for storing sets of COWList that must not overlap
    as prefixes, while supporting fast lookup, insertion, deletion, and sorted iteration.

    Attributes:
        prefix_free_sorted_trie_root (PrefixFreeSortedTrieNode[T]): The root of the underlying prefix trie.
        sorted_cowlist_set (SortedSet[COWList[T]]): A sorted set sorting all COWList.
    """
    __slots__ = ('prefix_free_sorted_trie_root', 'sorted_cowlist_set')

    def __init__(self, iterable=()):
        # type: (Iterable[COWList[T]]) -> None
        self.prefix_free_sorted_trie_root = PrefixFreeSortedTrieNode()  # type: PrefixFreeSortedTrieNode[T]
        self.sorted_cowlist_set = SortedSet()
        for cowlist in iterable:
            self.add(cowlist)

    def __contains__(self, item):
        return self.sorted_cowlist_set.__contains__(item)

    def __getitem__(self, index):
        return self.sorted_cowlist_set.__getitem__(index)

    def __iter__(self):
        return self.sorted_cowlist_set.__iter__()

    def __len__(self):
        return self.sorted_cowlist_set.__len__()

    def __reversed__(self):
        return self.sorted_cowlist_set.__reversed__()

    def add(self, cowlist):
        # type: (COWList[T]) -> bool
        """
        Attempt to add a COWList to the collection.

        - The COWList is only added if, after insertion, all COWList remain prefix-free;
          that is, neither the new COWList nor any current COWList is a prefix of the other.
        - If insertion is successful, the set of COWList is maintained in sorted order.

        Args:
            cowlist (COWList[T]): The COWList to add.

        Returns:
            bool: True if the COWList was added (did not violate prefix-freeness), False otherwise.
        """
        terminal_trie_node_or_none = add(self.prefix_free_sorted_trie_root, PutBackIterator(cowlist))
        if terminal_trie_node_or_none is not None:
            self.sorted_cowlist_set.add(cowlist)
            return True
        else:
            return False

    def discard(self, cowlist):
        # type: (COWList[T]) -> bool
        """
        Remove a COWList from the collection, if present.

        This operation maintains the prefix-free invariant and sorted order.

        Args:
            cowlist (COWList[T]): The COWList to remove.

        Returns:
            bool: True if the COWList was found and removed, False otherwise.
        """
        is_discarded = discard(self.prefix_free_sorted_trie_root, PutBackIterator(cowlist))
        if is_discarded:
            self.sorted_cowlist_set.discard(cowlist)
            return True
        else:
            return False
