from config_iso import choice, digits

def getracenumber():
    code = list()
    for i in range(6):
        code.append(choice(digits))
    unique_id=''.join(code) 
    return unique_id 