# batch-isbn
# Batch ISBN Fetcher
A script for batch acquiring book isbn using Open Library APIs
## known bugs
- Cannot handle non-ASCII inputs (Chinese, etc.)
- Multiple authors
- <del>Same character with different alias -> Just pick the one with highest similarity</del>
- Publisher error: correct is <i>WLC book</i>, in the found field, there are <i> W L C </i> and <i> SMK book</i>. The fuzzy match consider the latter a better match -> modify the heuristic function?
- This script <u>DOES NOT GUARANTEE ACCURACY!</u>
- Year must be 4-digit integer
## TO-DOs:
- [ ] Implement async and multithread queries
- [ ] More flexible input format
- [ ] Thorough Doccumentation