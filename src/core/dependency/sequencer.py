# /src/core/dependency/sequencer.py

"""Operation sequencing based on dependency graph."""

import copy
import uuid
from typing import Dict, List, Set
from schemas.dependency import (
    OperationDependencyGraph,
    OperationSequence,
    OperationSequenceCollection,
)


class OperationSequencer:
    """
    Core component for generating operation sequences from dependency graphs.

    Creates valid sequences of API operations based on their dependencies.
    """

    def generate_sequences(
        self,
        odg: OperationDependencyGraph,
        max_sequence_length: int = 10,
        max_sequences: int = 20,
    ) -> OperationSequenceCollection:
        """
        Generate operation sequences from a dependency graph.

        Args:
            odg: Operation Dependency Graph
            max_sequence_length: Maximum length of generated sequences
            max_sequences: Maximum number of sequences to generate

        Returns:
            Collection of operation sequences
        """
        sequence_lists = []

        # Build adjacency list for easier traversal
        graph = self._build_adjacency_list(odg)

        # Get nodes with no incoming edges (starting points)
        start_nodes = self._find_start_nodes(odg)

        # If no clear starting points, use all nodes
        if not start_nodes:
            start_nodes = odg.nodes

        # Generate sequences starting from each start node
        for start_node in start_nodes:
            new_sequences = self._dfs_sequences(graph, start_node, max_sequence_length)
            sequence_lists.extend(new_sequences)

            # Limit number of sequences
            if len(sequence_lists) >= max_sequences:
                sequence_lists = sequence_lists[:max_sequences]
                break

        # Convert to OperationSequence objects
        sequences = [
            OperationSequence(sequence_id=f"sequence-{uuid.uuid4()}", operations=seq)
            for seq in sequence_lists
        ]

        # Return as a collection
        return OperationSequenceCollection(operation_sequences=sequences)

    def _build_adjacency_list(
        self, odg: OperationDependencyGraph
    ) -> Dict[str, List[str]]:
        """Build adjacency list from ODG edges."""
        graph = {node: [] for node in odg.nodes}

        for edge in odg.edges:
            src = edge.src_operation_id
            dst = edge.dst_operation_id
            if src in graph and dst not in graph[src]:
                graph[src].append(dst)

        return graph

    def _find_start_nodes(self, odg: OperationDependencyGraph) -> List[str]:
        """Find nodes with no incoming edges."""
        # Build set of all destination nodes
        dest_nodes = set()
        for edge in odg.edges:
            dest_nodes.add(edge.dst_operation_id)

        # Find nodes that are not destinations
        start_nodes = [node for node in odg.nodes if node not in dest_nodes]
        return start_nodes

    def _dfs_sequences(
        self,
        graph: Dict[str, List[str]],
        start: str,
        max_length: int,
        visited: Set[str] = None,
        current_path: List[str] = None,
    ) -> List[List[str]]:
        """Generate sequences using DFS traversal."""
        if visited is None:
            visited = set()
        if current_path is None:
            current_path = []

        # Add current node to path
        current_path.append(start)
        visited.add(start)

        sequences = []

        # If path is long enough, add it
        if len(current_path) >= 2:  # Must have at least 2 operations
            sequences.append(copy.deepcopy(current_path))

        # Continue traversal if path not too long
        if len(current_path) < max_length:
            for neighbor in graph.get(start, []):
                if neighbor not in visited:
                    new_seqs = self._dfs_sequences(
                        graph, neighbor, max_length, visited.copy(), current_path.copy()
                    )
                    sequences.extend(new_seqs)

        return sequences
