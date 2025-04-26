# Tracker file to track every result of each run

_Note:_ 

**Accuracy** = Correct Predictions / Total Predictions

**Precision** = TP / (TP + FP) 
  - tells you: _Of all patients predicted Sick, how many are really Sick?_

**Recall** **(Sensitivity)** = TP / (TP + FN) 
  - tells you: _Of all actual Sick patients, how many did we catch?_

**F1-Score** = 2 × (Precision × Recall) / (Precision + Recall) 
  - the **balance** between Precision and Recall

## Run #1
|         | Training | Validation |
|---------|----------|------------|
| Healthy |   30     |     4      |
|  Sick   |   10     |     4      |

### Results
| Category | Accuracy | ROC Value | Precision | Recall | F1-Score |
|----------|--------------|-----------|--------|--------|---------|
| Eye   |  197/340 = **0.58**  |  0.62  | 0.21 | 0.29 | 0.24 |
| Mouth | 66/170 = **0.39** | 0.37 | 0.23 | 0.68 | 0.34 |
| Nose | 51/170 = **0.30** | 0.37 | 0.24 | 0.93 | 0.38 |
| Skin | 89/170 = **0.52** | 0.57 | 0.21 | 0.38 | 0.27 |
| Stacked | 102/187 = **0.55** | 0.45| 0.26 | 0.52 | 0.35 |



## Run #2 (Increased training set)
|         | Training | Validation |
|---------|----------|------------|
| Healthy |   56     |     4      |
|  Sick   |   36     |     4      |

### Results
| Category | Accuracy | ROC Value | Precision | Recall | F1-Score |
|----------|--------------|-----------|--------|--------|---------|
| Eye   |  200/340 = **0.59**  |  0.96  | 0.28 | 0.46 | 0.35 |
| Mouth | 84/170 = **0.49** | 0.89 | 0.23 | 0.50 | 0.32 |
| Nose | 95/170 = **0.56** | 0.80 | 0.27 | 0.50 | 0.35 |
| Skin | 113/170 = **0.66** | 0.70 | 0.31 | 0.35 | 0.33 |
| Stacked | 101/187 = **0.54** | 0.64| 0.24 | 0.43 | 0.31 |



## ReRun #2 with larger validation set
|         | Training | Validation |
|---------|----------|------------|
| Healthy |   56     |     35      |
|  Sick   |   36     |     35      |

### Results
| Category | Accuracy | ROC Value | Precision | Recall | F1-Score |
|----------|--------------|-----------|--------|--------|---------|
| Stacked | 36/70 = 0.51 | 0.13| 1 | 0.03 | 0.06 |



## Run #3 (Increased training set)
|         | Training | Validation |
|---------|----------|------------|
| Healthy |   92     |     35      |
|  Sick   |   104 (69 AI Generated)  |   35   |

### Results
| Category | Accuracy | ROC Value | Precision | Recall | F1-Score |
|----------|--------------|-----------|--------|--------|---------|
| Eye   |  764/1400 = **0.55**  |  0.93  | 0.54 | 0.60 | 0.57 |
| Mouth | 386/700 = **0.55** | 0.92 | 0.55 | 0.57 | 0.56 |
| Nose | 399/700 = **0.57** | 0.86 | 0.57 | 0.55 | 0.56 |
| Skin | 417/700 = **0.60** | 0.98 | 0.59 | 0.62 | **0.61** |
| Stacked | 440/770 = **0.57** | 0.87| 0.57 | 0.58 | 0.57 |



## Run #4 (Increased training healthy)
|         | Training | Validation |
|---------|----------|------------|
| Healthy |   126     |     35      |
|  Sick   |   104 (69 AI Generated)  |   35   |

### Results
| Category | Accuracy | ROC Value | Precision | Recall | F1-Score |
|----------|--------------|-----------|--------|--------|---------|
| Eye   |  721/1400 = **0.52**  |  0.97  | 0.51 | 0.69 | 0.59 |
| Mouth | 426/700 = **0.61** | 0.92 | 0.59 | 0.69 | **0.66** |
| Nose | 381/700 = **0.54** | 0.81 | 0.54 | 0.55 | 0.55 |
| Skin | 414/700 = **0.59** | 0.89 | 0.59 | 0.63 | 0.60 |
| Stacked | 416/770 = **0.54** | 0.90| 0.54 | 0.50 | 0.52 |



