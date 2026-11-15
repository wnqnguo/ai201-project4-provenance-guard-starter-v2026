# Capstone run: after

Produced by `capstone_run.py::main` on 2026-11-15_1448. Raw output: `capstone_2026-11-15_1448_after.json`.

| Criterion | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| 1. 12 bad inputs get a 400 with a message | 12/12 | 12/12 | 12/12 |
| 2. 10 French/Spanish sentences get a 400 | 8/10 | 8/10 | 8/10 |
| 3. 22 refusals logged with input and duration_ms | 17/22 | 17/22 | 17/22 |
| 4. 10 of my own paragraphs are scored, not refused | 9/10 | 9/10 | 9/10 |
| 5. 10 warm scored requests under 3 seconds | 9/10 | 9/10 | 9/10 |

## Misses by trial (input ids)

- Trial 1: c1 [], c2 ['ES2', 'ES4'], c3 not logged ['NEW1', 'NEW2', 'NEW3', 'ES2', 'ES4'], c4 ['N7'], c5 durations_ms [107.4, 83.1, 195.4, 83.0, 230.9, 370.7, 68.8, 65.9, 67.7]
- Trial 2: c1 [], c2 ['ES2', 'ES4'], c3 not logged ['NEW1', 'NEW2', 'NEW3', 'ES2', 'ES4'], c4 ['N7'], c5 durations_ms [109.1, 81.3, 247.6, 73.5, 183.6, 334.7, 68.4, 66.5, 67.7]
- Trial 3: c1 [], c2 ['ES2', 'ES4'], c3 not logged ['NEW1', 'NEW2', 'NEW3', 'ES2', 'ES4'], c4 ['N7'], c5 durations_ms [103.2, 77.9, 203.0, 72.8, 165.7, 339.7, 91.8, 69.0, 75.7]
