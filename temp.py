import math
base = 1.3
for i in range(2, 11):
    a = math.pow(base, i) / math.pow(base, 1)
    b = 1 / a
    print(i, 1, a, b)
