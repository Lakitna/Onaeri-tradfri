def printError(string):
    print("\033[1;31m%s\033[0;0m" % string)
def printWarning(string):
    print("\033[1;34m%s\033[0;0m" % string)
def printDone():
    print("\033[0;32m%s\033[0;0m" % "Done")


def scale(val, inRange, outRange, decimals=1):
    """
    Scale the given value from one scale to another
    """
    ret = ( (val - inRange[0]) \
            / (inRange[1] - inRange[0]) ) \
            * (outRange[1] - outRange[0]) \
            + outRange[0]

    if ret % 1 == 0:
        ret = round(ret)
    elif decimals > 0:
        ret = round(ret * (10*decimals)) / (10*decimals)
    else:
        ret = round(ret)

    return ret


def limitTo(val, rnge):
    if val < rnge[0]:  val = rnge[0]
    if val > rnge[1]:  val = rnge[1]
    return val


def sequenceResize(source, length):
    """
    Crude way of resizing a data sequence. Shrinking is here more accurate than expanding.
    """
    sourceLen = len(source)
    out = []
    for i in range(length):
        key = round(i * (sourceLen/length))
        if key >= sourceLen:
            key = sourceLen-1

        out.append(source[key])
    return out


def inRange(val, rnge):
    """
    Validate input value
    """
    if rnge[0] <= val <= rnge[1]:
        return True
    return False
