# DSB6: MovieLens Analytics + PyTest 🎓

What it's about
---------------
An analytical report on a 1000-record sample of the MovieLens dataset, built entirely on top of a custom OOP module `movielens_analysis.py`. The module exposes four classes (`Movies`, `Ratings`, `Tags`, `Links`) that parse the raw CSV files, compute statistics, and return sorted results. Every method is covered by a PyTest suite. The Jupyter report tells the story of the dataset in an interactive, chapter-based format, with every cell wrapped in `%timeit` to show how fast each step runs.

This was a collaborative project. My primary contribution was assembling the modules produced by the team into a single coherent notebook — I was responsible for the report structure, the narrative, the `%timeit` integration, and making sure every method from `movielens_analysis.py` was used at least once.

Stack
-----
- **Data Parsing:** `csv`, `re`, `collections`
- **Data Analysis:** Pandas, NumPy
- **Testing:** PyTest
- **Reporting:** Jupyter Notebook, `%timeit`

Results
-------
The dataset sample contains 1000 movies, 1000 ratings, 1000 tags, and 1000 links. Key findings from the report:

| Metric                                   | Value  |
|------------------------------------------|--------|
| **Movies with a parsed year**            | 761 / 1000 |
| **Oldest movie in the sample**           | 1931   |
| **Top genre (by film count)**            | Drama — 438 |
| **Unique users (ratings)**               | 7      |
| **Unique movies (ratings)**              | 802    |
| **Average rating**                       | 3.67   |
| **Rating range**                         | 0.5 – 5.0 |
| **Unique users (tags)**                  | 43     |
| **Most popular tag**                     | `funny` — 15 |
| **Movies with `tmdbId`**                 | 998 / 1000 |
| **Movies without `tmdbId`**              | 2      |
| **Links with missing external IDs**      | 301    |
| **PyTest tests (all passing)**           | yep |

Top-3 movies by weighted rating:

| Rank | `movieId` | Weighted rating | Avg rating | # ratings |
|------|-----------|-----------------|------------|-----------|
| 1    | 260       | 4.61            | 5.0        | 3         |
| 2    | 457       | 4.49            | 4.75       | 4         |
| 3    | 919       | 4.49            | 5.0        | 2         |

Pipeline
--------
1. **Data loading:** four CSV files from the `ml-latest-small` MovieLens sample (first 1000 records each) are parsed by the `Movies`, `Ratings`, `Tags`, and `Links` classes.
2. **Module design:** each class encapsulates its own file, exposes mandatory methods (`get_summary_stats`, `get_stats`, `get_top_movies`, `get_most_popular_tags`, `get_movies_without_tmdb`, `find_missing_ids`, etc.), and returns sorted, typed results.
3. **Testing:** a PyTest suite verifies return types, element types inside lists, and sorting correctness for every method. Tests are run before the report is generated.
4. **Reporting:** the notebook uses only classes from `movielens_analysis.py` — all other imports are pre-moved into the module. Every cell starts with `%%timeit -n 1 -r 1 -q`, so each analytical step is timed.
5. **Story:** the report is structured as a three-act "cinema visit" — entering the dark, voices in the dark, and the final credits — each act built on top of one or two classes.

Lessons learned
---------------
- **Encapsulation pays off:** keeping all parsing and statistics inside four classes made the notebook cells tiny and readable — every cell is one or two method calls plus a `print`.
- **Tests before the report:** writing PyTest checks for return types and sorting *before* writing the notebook saved hours of debugging later — broken sorting is hard to spot visually but trivial to catch with `assert`.
- **`%timeit` as a design constraint:** forcing every cell to be a single `%timeit` run pushed the team towards clean, side-effect-free methods.
- **Narrative matters:** a report with a story (three acts, characters, a closing line) reads very differently from a wall of numbers — and it makes the technical results stick.
- **Working with teammates' code:** integrating modules written by different people required reading their code carefully and agreeing on a shared interface before merging.

How to run
----------
Install dependencies and make sure the `ml-latest-small` sample is in `./ml-latest-small/`. Then:

```bash
# 1. Run the test suite
pytest -q

# 2. Open the report
jupyter notebook movielens_report.ipynb
