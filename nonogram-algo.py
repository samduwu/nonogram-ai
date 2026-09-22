# This is a placeholder file to help show how PRs should be structured
# Down the line this file can be moved/updated to fit proper algorithm needs

def nanogram_algo(column, rows):
    ...
    # Columns might be easier to handle as nested lists; so for a nonogram with columns -
    # 3
    # 1 2 3 2 2

    # The corresponding lists could look like
    # [
    #  [3, 0, 0, 0, 0],
    #  [1, 2, 3, 2, 2],
    # ]

    # Similarly, for a nonogram with rows -
    #   4
    #   4
    # 1 1
    #   1
    #   1

    # The corresponding lists could look like
    # [
    #  [0, 4],
    #  [0, 4],
    #  [1, 1],
    #  [0, 1],
    #  [0, 1],
    # ]

    # Determine dimensions of grid and generate a final solution variable
    solution = []

    # Apply logic to iterate through each row and column to determine which spaces are filled or not

    # Return a completed grid where
    # 0 - blank space 
    # 1 - indicates a filled in space

    return solution