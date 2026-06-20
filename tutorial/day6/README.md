# Tutorial Day 6: Search and State Modeling

## Why this day matters
Pathfinding, graph traversal, and grid walks show up repeatedly in AoC.

## Focus Topics
- Representing nodes and edges
- DFS/BFS style recursion
- Visited sets to avoid loops

## Learning Goals
- Implement a small graph traversal.
- Prevent infinite recursion on cyclic graphs.

## REPL Drills
```prolog
?- edge(a,b).
?- path(a, d, P).
```

## Verification
- Test cyclic graph safety.
- Test shortest/any-path behavior depending on implementation.

## Exit Criteria
- You can model state transitions as predicates cleanly.
