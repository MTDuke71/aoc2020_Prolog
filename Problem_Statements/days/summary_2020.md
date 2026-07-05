# AoC 2020 Summary

| Day | Status | Part 1 | Part 2 | Notes |
|---:|---|---:|---:|---|
| 00 | ✅ | 3481005 | 5218616 | Tutorial dry run (Rocket Equation); `maplist`/`sum_list`, recursive `total_fuel/2`. 7/7 tests pass. |
| 01 | ✅ | 902451 | 85555470 | Report Repair; k-SUM via nondeterministic `k_sum/4` (take/skip DFS with `X =< Target` pruning on `msort`ed input), `once/1` + `foldl` product. 8/8 tests pass. |
| 02 | ✅ | 460 | 251 | Password Philosophy; first DCG parse (`entry//1` via `dcg/basics`) into `entry/4` records, policies as predicates counted with `include/3`, XOR via if-then-else. 11/11 tests pass. |
