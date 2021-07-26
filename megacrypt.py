import random
abc = [
'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
'а','б','в','г','д','е','ё','ж','з','и','й','к','л','м','н','о','п','р','с','т','у','ф','х','ц','ч','ш','щ','ъ','ы','ь','э','ю','я',
'А','Б','В','Г','Д','Е','Ё','Ж','З','И','Й','К','Л','М','Н','О','П','Р','С','Т','У','Ф','Х','Ц','Ч','Ш','Щ','Ъ','Ы','Ь','Э','Ю','Я',
'1','2','3','4','5','6','7','8','9','0',
'!','@',',','.','?','/','%','*','+','-','=',' ',"'",'"',')','(','_','|'
]
def getSymbol(symbol, offset, abc):
    if symbol not in abc:
        return symbol
    index = abc.index(symbol)
    newIndex = index + offset
    while newIndex >= len(abc):
        newIndex -= len(abc)
    while newIndex < 0:
        newIndex += len(abc)
    return abc[newIndex]

def megaCrypt(msg):
    if msg == "":
        return "Сообщение не распознано"
    seed = random.randint(10,99)
    out = getSymbol(msg[0], seed, abc)
    for i in range(1, len(msg)):
        temp = getSymbol(msg[i], abc.index(out[i - 1]), abc)
        out += getSymbol(temp, (seed - i), abc)
    return out + str(seed)

def megaDecrypt(msg):
    if len(msg) <= 2:
        return "Сообщение не распознано"
    try:
        seed = int(msg[-2:])
    except:
        return "Сообщение не распознано"
    out = getSymbol(msg[0], -seed, abc)
    for i in range(1, len(msg) - 2):
        temp = getSymbol(msg[i], -abc.index(msg[i - 1]), abc)
        out += getSymbol(temp, -(seed - i), abc)
    return out
