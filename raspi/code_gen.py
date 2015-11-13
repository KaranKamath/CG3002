
def printvals(n):
    for i in range(n):
        s = str(i+1)
        if len(s) == 1:
            s = '0' + s
        s += s + s
        print s

printvals(40)
printvals(20)
printvals(16)
