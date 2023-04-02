from gurobipy import *
import math
import pandas as pd

### PATTERNS ###
# 1 - BLUE STAR YELLOW BACKGROUND
# 2 - YELLOW STAR MAROON BACKGROUND
# 3 - PINK DIAMOND BLUE BACKGROUND
# 4 - DARK BLUE CROSS, PINK SURROUNDING
# 5 - ORANGE DILDO
# 6 - PINK DILDO
# 7 - PURPLE STAR ORANGE BACKGROUND
# 8 - MAROON CROSS GREEN SURROUND
# 9 - BLUE DIAMOND PURPLE BACKGROUND
# 10 - LIGHT BLUE TRIANGLE DARK BLUE BACKGROUND
# 11 - GREEN TRIANGLE YELLOW BACKGROUND
# 12 - YELLOW PATCH PINK BACKGROUND
# 13 - DARK BLUE PATCH YELLOW BACKGROUND
# 14 - PURPLE CROSS, YELLOW SURROUND
# 15 - ORANGE DIAMOND GREEN BACKGROUND
# 16 - PINK PATCH BLUE BACKGROUND
# 17 - BLUE BRACKET PINK BACKGROUND
# 18 - YELLOW DIDLO
# 19 - ORANGE SMOOTH BRACKET
# 20 - YELLOW FLOWER
# 21 - LIGHT BLUE AXE
# 22 - DARK BLUE HEXAGON


df = pd.read_csv('pieces.csv', sep=',')

def gen_orientations(o):
    return [o,[o[1],o[2],o[3],o[0]],[o[2],o[3],o[0],o[1]],[o[3],o[0],o[1],o[2]]]

# Piece encodings
piece_encodings = {}
raw_data = dict(zip(df['index'], df['piece']))

for piece in raw_data:
    list_form = raw_data.get(piece).split(';')

    new_list = []
    for num in list_form:
        if int(num) not in range(-1,23):
            print('invalid piece encoding', int(num))
        else:
            new_list.append(int(num))

    piece_encodings[piece] = gen_orientations(new_list)

S = range(len([p for p in piece_encodings if -1 in piece_encodings.get(p)]))
R = range(int(math.sqrt(len(piece_encodings))))
C = range(int(math.sqrt(len(piece_encodings))))

P = range(len(piece_encodings))
O = range(len(piece_encodings.get(1)))

m = Model()

# 1 if piece p fits in position (i,j) in orientation o
X = {(i,j,p,o) : m.addVar(vtype = GRB.BINARY) for i in R for j in C for p in P for o in O}

# Only 1 piece per square
for i in R:
    for j in C:
        m.addConstr(quicksum(X[i,j,p,o] for p in P for o in O) == 1)

# Piece can only be used once
for p in P:
    m.addConstr(quicksum(X[i,j,p,o] for i in R for j in C for o in O) == 1)

# Neighbour Constraint Column
for i in R:
    for j in C[:-1]:
        m.addConstr(quicksum(X[i,j,p,o] * piece_encodings[p][o][1] for p in P for o in O) == 
                    quicksum(X[i,j+1,p,o] * piece_encodings[p][o][3] for p in P for o in O))

# Neighbour Constraint Row
for j in C:
    for i in R[:-1]:
        m.addConstr(quicksum(X[i,j,p,o] * piece_encodings[p][o][2] for p in P for o in O) == 
                    quicksum(X[i+1,j,p,o] * piece_encodings[p][o][0] for p in P for o in O))
        
# Constrain Side Pieces (Row)
for i in R:
    if i == 0:
        m.addConstr(quicksum(X[i,j,p,o] * piece_encodings[p][o][0] for p in P for o in O) == -1)
    if i == R[:-1]:
        m.addConstr(quicksum(X[i,j,p,o] * piece_encodings[p][o][2] for p in P for o in O) == -1)

# Constrain Side Pieces (Col)
for j in C:
    if j == 0:
        m.addConstr(quicksum(X[i,j,p,o] * piece_encodings[p][o][3] for p in P for o in O) == -1)
    if j == C[:-1]:
        m.addConstr(quicksum(X[i,j,p,o] * piece_encodings[p][o][1] for p in P for o in O) == -1)

m.optimize()


result = ""
for i in R:
    for j in C:
        for p in P:
             for o in O:
                if X[i,j,p,o].x > 0:
                    result += "(p:{}, o:{})".format(p+1, o)
                    if j == len(R)-1:
                        result += '\n'
print(result)




