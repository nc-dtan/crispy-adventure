from itertools import combinations


def find_target_sum(target, numbers, nmax=5):
    """Find the target sum in all combinations of a list.

    Input
    -----
    target: float
      The target sum
    numbers: list
      List of floats, e.g. IR
    nmax: int (default is 5)
      The max length of the list of combinations. E.g. if 3, then
      the list of combinations will have length of 1, 2, and 3.

    Output
    ------
    res: list
      The list of combinations which sum gives the target sum
    """
    if target in numbers:
        return [target]

    for r in range(2, nmax+1):  # [2, 3, ..., namx]
        for combination in combinations(numbers, r):
            if sum(combination) == target:
                return list(combination)