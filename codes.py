import random

def jobs_random():
    num = []
    for i in range(0, 8):
        num.append(i)
    
    number = []
    for i in range(0, 8):
        number.append(num.pop(num.index(random.choice(num))))
    
    return number