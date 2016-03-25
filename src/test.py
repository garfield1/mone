def d(i):
    a = 1
    s = 0
    while a <= i:
        if i % a == 0:
            s = s + a
        a = a + 1
    return s

print d(4)