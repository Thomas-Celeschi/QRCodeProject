class ReedSolomon:
    # Galois fields
    # -- exponents (anti-logarithms)
    __GFEXP = [0] * 512

    # -- logarithms
    __GFLOG = [0] * 256

    # INITIALISATION CONSTRUCTOR
    def __init__(self):
        # prepare the exponential and logarithmic fields
        self.__GFEXP[0] = 1
        byteValu = 1
        for bytePos in range(1, 255):
            byteValu <<= 1
            if (byteValu & 0x100):
                byteValu ^= 0x11d

            # update the field elements
            self.__GFEXP[bytePos] = byteValu
            self.__GFLOG[byteValu] = bytePos

        # finalise the exponential field
        for bytePos in range(255, 512):
            self.__GFEXP[bytePos] = self.__GFEXP[bytePos - 255]

    ## GALOIS PRIMITIVE OPERATIONS
    # -----
    # Galois multiplication
    # argX, argY: multiplicand, multiplier
    # byteValu: product
    def __gfMult(self, argX, argY):
        # parametre checks
        if ((argX == 0) or (argY == 0)):
            byteValu = 0
        else:
            # perform the operation
            byteValu = self.__GFLOG[argX]
            byteValu += self.__GFLOG[argY]
            byteValu = self.__GFEXP[byteValu]

        # return the product result
        return (byteValu)

    # Galois division
    # argX, argY: dividend, divisor
    # byteValu: quotient
    def __gfDivi(self, argX, argY):
        # validate the divisor
        if (argY == 0):
            raise ZeroDivisionError()

        # validate the dividend
        if (argX == 0):
            byteValu = 0
        else:
            # perform the division
            byteValu = self.__GFLOG[argX] - self.__GFLOG[argY]
            byteValu += 255
            byteValu = self.__GFEXP[byteValu]

        # return the division result
        return (byteValu)

    ## GALOIS POLYNOMIAL OPERATIONS
    # -----
    # Polynomial addition
    # polyA, polyB: polynomial addends
    # polySum: polynomial sum
    def _gfPolyAdd(self, polyA, polyB):
        # initialise the polynomial sum
        polySum = [0] * max(len(polyA), len(polyB))

        # process the first addend
        for polyPos in range(0, len(polyA)):
            polySum[polyPos + len(polySum) - len(polyA)] = polyA[polyPos]

        # add the second addend
        for polyPos in range(0, len(polyB)):
            polySum[polyPos + len(polySum) - len(polyB)] ^= polyB[polyPos]

        # return the sum
        return (polySum)

    # Polynomial multiplication
    # polyA, polyB: polynomial factors
    # polyProd: polynomial product
    def _gfPolyMult(self, polyA, polyB):
        # initialise the product
        polyProd = len(polyA) + len(polyB) - 1
        polyProd = [0] * polyProd

        # start multiplying
        for posB in range(0, len(polyB)):
            for posA in range(0, len(polyA)):
                polyProd[posA + posB] ^= self.__gfMult(polyA[posA], polyB[posB])

        # return the product result
        return (polyProd)

    # Polynomial scaling
    # argPoly: polynomial argument
    # argX: scaling factor
    # polyVal: scaled polynomial
    def _gfPolyScale(self, argPoly, argX):
        # initialise the scaled polynomial
        polyVal = [0] * len(argPoly)

        # start scaling
        for polyPos in range(0, len(argPoly)):
            polyVal[polyPos] = self.__gfMult(argPoly[polyPos], argX)

        # return the scaled polynomial
        return (polyVal)

    # Polynomial evaluation
    # argPoly: polynomial argument
    # argX: independent variable
    # byteValu: dependent variable
    def _gfPolyEval(self, argPoly, argX):
        # initialise the polynomial result
        byteValu = argPoly[0]

        # evaluate the polynomial argument
        for polyPos in range(1, len(argPoly)):
            tempValu = self.__gfMult(byteValu, argX)
            tempValu = tempValu ^ argPoly[polyPos]
            byteValu = tempValu

        # return the evaluated result
        return (byteValu)

    ## REED-SOLOMON SUPPORT ROUTINES
    # -----
    # Prepare the generator polynomial
    # errSize: number of error symbols
    # polyValu: generator polynomial
    def _rsGenPoly(self, errSize):
        polyValu = [1]

        for polyPos in range(0, errSize):
            tempVal = [1, self.__GFEXP[polyPos]]
            polyValu = self._gfPolyMult(polyValu, tempVal)

        # return the polynomial result
        return (polyValu)

    ## REED-SOLOMON ENCODING
    # ------
    # argMesg: the message block
    # errSize: number of error symbols
    # outBuffer: the encoded output buffer
    def RSEncode(self, argMesg, errSize):

        # prepare the generator polynomial
        polyGen = self._rsGenPoly(errSize)

        # prepare the output buffer
        outBuffer = (len(argMesg) + errSize)
        outBuffer = [0] * outBuffer

        # initialise the output buffer
        for mesgPos in range(0, len(argMesg)):
            mesgChar = argMesg[mesgPos]
            outBuffer[mesgPos] = ord(mesgChar)

        # begin encoding
        for mesgPos in range(0, len(argMesg)):
            mesgChar = outBuffer[mesgPos]
            if (mesgChar != 0):
                for polyPos in range(0, len(polyGen)):
                    tempValu = self.__gfMult(polyGen[polyPos], mesgChar)
                    outBuffer[mesgPos + polyPos] ^= tempValu

        # finalise the output buffer
        for mesgPos in range(0, len(argMesg)):
            mesgChar = argMesg[mesgPos]
            outBuffer[mesgPos] = ord(mesgChar)

        # return the output buffer
        return (outBuffer)


#tranforme un tableau de décimal en tableau de binaire
def DecimalToBinary(Tab):
    for pos in range(len(Tab)):
        bnum = Tab[pos]
        dnum = 0
        val = 1
        while bnum != 0:
            rem = bnum % 2
            dnum = dnum + (rem * val)
            val = val * 10
            bnum = int(bnum / 2)
        Tab[pos] = dnum
    return Tab

testRS = ReedSolomon()

Mesg = "Test message"  # Symboles de message
Size = 12  # Taille des symboles de message

# encode the message
dCode = testRS.RSEncode(Mesg, Size)   #tCode est le tableau de décimal après RS
print("tableau de décimal : ", dCode)

bCode = DecimalToBinary(dCode)  #bCode est le tableau de binaire après RS
print("Tableau de binaire : ", bCode)
# print(tCode.DecimalToBinary(tCode))
