import pyAesCrypt 
import pickle 
import os

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        self.balance = 1
        self.status = 0 #0: Voter, 1: Candidate

    def __repr__(self):
        return f'<Username: {self.username}, User ID: {self.id}>'

KEY = "9t1Wf_vajA0RoYD5s2YyHymbvJB27E2CFYK1Rv0MK9Y="

def load_data():
    users = []
    pyAesCrypt.decryptFile("UserData.pkl.aes","UserData.pkl",KEY)
    with open("UserData.pkl","rb") as filehandle:
        users = pickle.load(filehandle)
    if os.path.isfile("UserData.pkl"):
        os.remove("UserData.pkl")
    return users

def encrypt_data(users):
    with open('UserData.pkl','wb') as filehandle:
        pickle.dump(users,filehandle)
    pyAesCrypt.encryptFile("UserData.pkl","UserData.pkl.aes",KEY)
    if os.path.isfile("UserData.pkl"):
        os.remove("UserData.pkl")
    
def basic_user_loading():
    users = []
    users.append(User(1000,"admin","admin"))
    users.append(User(1001,"Naman","secret"))
    users.append(User(1002,"Akshay","secret1"))
    users.append(User(1003,"Muskan","secret2"))
    users.append(User(1004,"Hardik","secret3"))
    users.append(User(1005,"Rijul","secret4"))
    users.append(User(1006,"Ritika","secret5"))

    with open('UserData.pkl','wb') as filehandle:
        pickle.dump(users,filehandle)
    pyAesCrypt.encryptFile("UserData.pkl","UserData.pkl.aes",KEY)
    if os.path.isfile("UserData.pkl"):
        os.remove("UserData.pkl")

if __name__ == "__main__":
    basic_user_loading()
