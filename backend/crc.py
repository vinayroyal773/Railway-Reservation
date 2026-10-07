def _xor(a, b):
    return ''.join('0' if x == y else '1' for x, y in zip(a, b))

def crc_remainder(data, generator):
    value = data + "0" * (len(generator) - 1)
    for i in range(len(data)):
        if value[i] == "1":
            value = value[:i] + _xor(value[i:i+len(generator)], generator) + value[i+len(generator):]
    return value[-(len(generator)-1):]

def crc_check(message, generator):
    remainder = crc_remainder(message, generator)
    codeword = message + remainder
    check = codeword
    for i in range(len(message)):
        if check[i] == "1":
            check = check[:i] + _xor(check[i:i+len(generator)], generator) + check[i+len(generator):]
    return {
        "message": message,
        "generator": generator,
        "crc": remainder,
        "codeword": codeword,
        "error_detected": "1" in check
    }
