import random

def get_user_agent():
    with open('user-agent.txt', 'r') as fObj:
        return random.choice(fObj.readlines())



if __name__ == '__main__':
    print(get_user_agent())