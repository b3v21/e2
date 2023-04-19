from gurobipy import *
import pandas as pd
from typing import *

### PATTERNS ###
# 1 - BLUE STAR YELLOW BACKGROUND
# 2 - YELLOW STAR MAROON BACKGROUND
# 7 - PURPLE STAR ORANGE BACKGROUND

# 3 - PINK DIAMOND BLUE BACKGROUND
# 9 - BLUE DIAMOND PURPLE BACKGROUND
# 15 - ORANGE DIAMOND GREEN BACKGROUND

# 4 - DARK BLUE CROSS, PINK SURROUNDING
# 8 - MAROON CROSS GREEN SURROUND
# 14 - PURPLE CROSS, YELLOW SURROUND

# 5 - ORANGE DILDO
# 6 - PINK DILDO
# 18 - YELLOW DIDLO

# 10 - LIGHT BLUE TRIANGLE DARK BLUE BACKGROUND
# 11 - GREEN TRIANGLE YELLOW BACKGROUND

# 12 - YELLOW PATCH PINK BACKGROUND
# 13 - DARK BLUE PATCH YELLOW BACKGROUND
# 16 - PINK PATCH BLUE BACKGROUND

# 17 - BLUE BRACKET PINK BACKGROUND
# 19 - ORANGE SMOOTH BRACKET
# 20 - YELLOW FLOWER
# 21 - LIGHT BLUE AXE
# 22 - DARK BLUE HEXAGON

PUZZLE_SIZE = 16


def eternity_two_solver(pieces: Dict[int, List[str]]):
    R = range(1, PUZZLE_SIZE + 1)  # set of row coordinates
    C = range(1, PUZZLE_SIZE + 1)  # set of columnn coordinate
    P = range(1, PUZZLE_SIZE * PUZZLE_SIZE + 1)  # set of pieces (1 to 256)
    O = range(4)  # set of orientations for each piece

    m = Model("Eternity 2 Solver")

    X = {
        (i, j, p): m.addVar(vtype=GRB.BINARY) for i in R for j in C for p in P
    }  # 1 if piece p is used in position (i,j)
    Y = {
        (o, p): m.addVar(vtype=GRB.BINARY) for o in O for p in P
    }  # 1 if piece p is placed in orientation o
    Z = {
        p: m.addVar(vtype=GRB.BINARY) for p in P
    }  # 1 if piece P is in the correct position

    # THESE HINTS COULD BE WRONG

    # hint 1: piece 139, orientation 2, position (8,8)
    m.addConstr(X[8, 8, 139] == 1)
    m.addConstr(Y[2, 139] == 1)

    # hint 2: piece 207, orientation 1 position (3,3)
    m.addConstr(X[3, 3, 207] == 1)
    m.addConstr(Y[1, 207] == 1)

    # hint 3: piece 254, orientation 3, position (3,14)
    m.addConstr(X[3, 14, 254] == 1)
    m.addConstr(Y[3, 254] == 1)

    # hint 4: piece 180, orientation 3, position (14,3)
    m.addConstr(X[14, 3, 180] == 1)
    m.addConstr(Y[3, 180] == 1)

    # hint 5: piece 248, orientation 0, position (14,4)
    m.addConstr(X[14, 14, 248] == 1)
    m.addConstr(Y[0, 248] == 1)

    # every piece must be used only once, in only one orientation
    for p in P:
        m.addConstr(quicksum(X[i, j, p] for i in R for j in C) == 1)
        m.addConstr(quicksum(Y[o, p] for o in O) == 1)

    # each piece must be in a different position
    for i in R:
        for j in C:
            m.addConstr(quicksum(X[i, j, p] for p in P) == 1)

    # Neighbour Constraint Column
    # for i in R:
    #     for j in C[:-1]:
    #         m.addConstr(
    #             quicksum(X[i, j, p] * piece_encodings[p][o][1] for p in P for o in O)
    #             == quicksum(
    #                 X[i, j + 1, p] * piece_encodings[p][o][3] for p in P for o in O
    #             )
    #         )

    # Neighbour Constraint Row
    # for j in C:
    #     for i in R[:-1]:
    #         m.addConstr(
    #             quicksum(X[i, j, p, o] * piece_encodings[p][o][2] for p in P for o in O)
    #             == quicksum(
    #                 X[i + 1, j, p, o] * piece_encodings[p][o][0] for p in P for o in O
    #             )
    #         )

    # Constrain Side Pieces (Row)
    # for i in R:
    #     if i == 0:
    #         m.addConstr(
    #             quicksum(X[i, j, p, o] * piece_encodings[p][o][0] for p in P for o in O)
    #             <= 0
    #         )
    #     if i == R[:-1]:
    #         m.addConstr(
    #             quicksum(X[i, j, p, o] * piece_encodings[p][o][2] for p in P for o in O)
    #             <= 0
    #         )

    # Constrain Side Pieces (Col)
    # for j in C:
    #     if j == 0:
    #         m.addConstr(
    #             quicksum(X[i, j, p, o] * piece_encodings[p][o][3] for p in P for o in O)
    #             <= 0
    #         )
    #     if j == C[:-1]:
    #         m.addConstr(
    #             quicksum(X[i, j, p, o] * piece_encodings[p][o][1] for p in P for o in O)
    #             <= 0
    #         )

    # objective is to maximize the number of correct placements
    m.setObjective(quicksum(Z[p] for p in P), GRB.MAXIMIZE)

    m.optimize()

    result = ""
    for i in R:
        for j in C:
            for p in P:
                if X[i, j, p].x == 1:
                    for o in O:
                        if Y[o, p].x == 1:
                            result += "(p:{}, o:{})".format(p, o)
                            if j == len(R) - 1:
                                result += "\n"
    print(result)


if __name__ == "__main__":
    # load in piece data
    df = pd.read_csv("pieces.csv", sep=",")
    pieces = [[eval(y) for y in x.split(";")] for x in df["piece"]]

    # check data is correct
    for piece in pieces:
        for edge in piece:
            if edge not in (list(range(1, 23)) + [-1]):
                print("invalid edge number", int(edge))

    eternity_two_solver(pieces)
