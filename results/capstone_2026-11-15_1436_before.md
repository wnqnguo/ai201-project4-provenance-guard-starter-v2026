# Capstone run: before

Produced by `capstone_run.py::main` on 2026-11-15_1436. Raw output: `capstone_2026-11-15_1436_before.json`.

| Criterion | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| 1. 12 bad inputs get a 400 with a message | 12/12 | 12/12 | 12/12 |
| 2. 10 French/Spanish sentences get a 400 | 0/10 | 0/10 | 0/10 |
| 3. 22 refusals logged with input and duration_ms | 9/22 | 9/22 | 9/22 |
| 4. 10 of my own paragraphs are scored, not refused | 10/10 | 10/10 | 10/10 |
| 5. 10 warm scored requests under 3 seconds | 10/10 | 10/10 | 10/10 |

## Misses by trial (input ids)

- Trial 1: c1 [], c2 ['FR1', 'FR2', 'FR3', 'FR4', 'FR5', 'ES1', 'ES2', 'ES3', 'ES4', 'ES5'], c3 not logged ['NEW1', 'NEW2', 'NEW3', 'FR1', 'FR2', 'FR3', 'FR4', 'FR5', 'ES1', 'ES2', 'ES3', 'ES4', 'ES5'], c4 [], c5 durations_ms [107.6, 80.8, 196.2, 75.1, 170.9, 390.2, 69.3, 67.8, 66.2, 67.5]
- Trial 2: c1 [], c2 ['FR1', 'FR2', 'FR3', 'FR4', 'FR5', 'ES1', 'ES2', 'ES3', 'ES4', 'ES5'], c3 not logged ['NEW1', 'NEW2', 'NEW3', 'FR1', 'FR2', 'FR3', 'FR4', 'FR5', 'ES1', 'ES2', 'ES3', 'ES4', 'ES5'], c4 [], c5 durations_ms [106.7, 78.9, 193.1, 74.1, 168.7, 353.7, 67.5, 70.3, 66.0, 67.0]
- Trial 3: c1 [], c2 ['FR1', 'FR2', 'FR3', 'FR4', 'FR5', 'ES1', 'ES2', 'ES3', 'ES4', 'ES5'], c3 not logged ['NEW1', 'NEW2', 'NEW3', 'FR1', 'FR2', 'FR3', 'FR4', 'FR5', 'ES1', 'ES2', 'ES3', 'ES4', 'ES5'], c4 [], c5 durations_ms [104.8, 80.4, 194.9, 72.8, 181.4, 358.9, 67.8, 70.4, 66.7, 76.3]
