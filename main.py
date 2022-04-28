import random 
import time
import threading
from tkinter.font import names
from flask import Flask, render_template, redirect, url_for, session, request
from datetime import datetime
from block import Block
from blockchain import Blockchain
from vote import Vote 
from user_data import User, load_data, encrypt_data

users = load_data()
flag_variable = True
lock = threading.Lock()
election_chain = Blockchain([])
names_list=[]

def verify_transaction(p,g,y,s,b,r):
    #y = pow(g,x,p) Sender's Public Value
    #s = (r+b*x)%(p-1) Calculated by Sender
    #b = int.from_bytes(random.randbytes(1),"big")
    #r = random.randint(0,p-1)
    h = pow(g,r,p)
    if pow(g,s,p) == (h*pow(y,b,p))%p:
        return True
    else: 
        return False

def mine_block():
    global election_chain
    lock.acquire()
    last_block = election_chain.previous_block()
    last_hash = last_block.get_block_hash()
    election_chain.new_block(last_hash)
    lock.release()

def return_users_string():
    temp_string = []
    for user in users: 
        temp_string.append(repr(user))
    """
    Note: User's voting status is not displayed to enhance 
    anonymity and enable free and fair elections.
    """
    return temp_string
  
app = Flask(__name__)
app.secret_key = 'BITSF463_Cryptography_Term_Project_Group19'


# Route for handling the login page logic
@app.route('/', methods=['GET', 'POST'])
def login():
    global user
    error = None
    session.pop('admin',None)
    if request.method == 'POST':
        session.pop('user',None)

        username = request.form['username']
        password = request.form['password']

        if len(username) < 4 or len(password)<4:
            error = 'Invalid Credentials. Please try again.'
            return redirect(url_for("login"))

        for x in users:
            if x.username == username:
                user = x
                if  username == 'admin' and password == 'admin':
                    session['admin'] = 'admin'
                    if Blockchain.status == 1:
                        return redirect(url_for('admin_home2'))
                    elif Blockchain.status == 0:
                        return redirect(url_for('admin_home'))
                elif username == user.username and password == user.password:
                    session['user_id'] = user.id
                    return redirect(url_for('user_home'))
        else:
            error = 'Invalid Credentials. Please try again.'

    return render_template('login.html', error=error)
 

@app.route('/login_successful', methods=['GET', 'POST'])
def user_home():
    global user, election_chain, names_list
    if 'user_id' not in session:
        return redirect(url_for('login'))
    error = None
    nameString=None
    candidature = None
    if Blockchain.status == 0 and user.status==0:
        if request.method=="POST":
            if request.form['Candidature'] == "Apply for Candidature":
                user.status = 1
                names_list.append(user.username)
                return redirect(url_for("user_home"))
        return render_template("profile_before.html")
    else:
        
        if user.status==1:
            candidature = "You've registered as a candidate for these elections."
        nameString = []
        for i in range(len(names_list)):
            nameString.append(str(i+1)+") "+names_list[i])
        
        if request.method == "POST":
            vote = Vote(request.form["vote"])
            if Blockchain.status == 0:
                error="The voting has not started yet."
            elif user.balance != 1:
                error = "You have already voted in this election."
            elif vote.check_vote():
                p,g,b=11,2,int.from_bytes(random.randbytes(1),"big")
                y = pow(g,int(vote.vote),p) #Sender's Public Value
                r = random.randint(0,p-1)
                s = (r+b*int(vote.vote))%(p-1) #Calculated by Sender
                if verify_transaction(p,g,y,s,b,r):
                    user.balance -=1
                    encrypt_data(users)
                    election_chain.unconfirmed_votes.append(vote)
                else:
                    print("Error, invalid transaction")
                return render_template("voted.html")
            else:
                error = "Invalid Vote String. Please enter a valid vote."
        return render_template("profile_after.html", error=error,nameString=nameString,candidature=candidature)


@app.route("/admin_setup", methods=["GET","POST"])
def admin_home():
    global election_chain, names_list
    for i in users:
        if i.status == 1 and i.username not in names_list:
            names_list.append(i.username)
    if 'admin' not in session:
        return redirect(url_for('login'))
    error,error2 = None,None
    candidates = None
    
    if len(names_list)==0:
        error2 = "No candidate has applied for candidature yet"
    else:
        candidates=names_list

    if request.method == "POST":
        if request.form["start_button"] == "Remove Candidate":
            name = request.form["candidate"]
            names_list.remove(name)
            for i in users:
                if i.username == name:
                    i.status = 0
            return redirect(url_for('admin_home'))
        elif request.form["start_button"] == "Start Elections":
            if len(names_list)>=2:
                lock.acquire()
                Vote.candidates = len(names_list)
                Blockchain.status = 1
                election_chain = Blockchain(names_list)
                lock.release()
                if t2.is_alive():
                    t2.join()
                t2.start()
                #print("Lock released")
                return redirect(url_for("admin_home2"))
            else:
                error = "Minimum Two candidates needed for elections."
        elif request.form["start_button"] == "LOGOUT":
            return redirect(url_for("login"))
        
    return render_template("admin_start.html", error=error,error2=error2,candidates=candidates)


@app.route("/admin_stop", methods=["GET","POST"])
def admin_home2():
    global flag_variable
    global election_chain
    if 'admin' not in session:
        return redirect(url_for('login'))
    if Blockchain.status == 0:
        return redirect(url_for("login"))
    value = None
    chain = None
    userString = None
    resultString=None
    if request.method == "POST":
        if request.form['button'] == "End Elections":
            #Mining Last Block
            last_block = election_chain.previous_block()
            last_hash = last_block.get_block_hash()
            election_chain.unconfirmed_votes.append("Election over at:"+str(datetime.now()))
            election_chain.new_block(last_hash)
            Blockchain.status = 0 #Disabling Further Voting
            #Resetting votes for Anonymity & preparing for next elections.
            for user in users: 
                user.balance = 1
                user.status = 0
            encrypt_data(users)
            flag_variable = False #Stopping Further Mining.
            value = "Elections Stopped!"
            #Preparing to display Blockchain.
            chain = []
            for block in election_chain.chain:
                chain.append(repr(block))
            results = election_chain.display_results()
            candidates = election_chain.candidates
            #Preparing to display Results.
            resultString = []
            for i in range(len(candidates)):
                resultString.append(candidates[i] +" has recieved "+ str(results[i])+" votes.")            
        elif request.form["button"] == "Show Blockchain":
            chain = []
            for block in election_chain.chain:
                chain.append(repr(block))
        elif request.form["button"] == "Mine Block":
            mine_block()
            return render_template("admin_stop.html",value=value, chain=chain, userString=userString, resultString=resultString)
        
        elif request.form["button"] == "View Users":
            userString=return_users_string()
    
    return render_template("admin_stop.html",value=value, chain=chain, userString=userString, resultString=resultString)

def main():
    app.run(debug=False)

def timed_miner():
    global flag_variable
    global election_chain
    starttime = time.time()
    print("\nMiner Started in Background.\n")
    while True:
        if not flag_variable:
            print("Breaking due to flag variable.")
            break
        if (Blockchain.status==1 and len(election_chain.unconfirmed_votes)!=0):
            mine_block()    
            print("Block Mined")
        time.sleep(30.0 - ((time.time() - starttime) % 30.0))
    print("\nMiner Stopped.\n")

if __name__ == "__main__":
    t1 = threading.Thread(target=main)
    t2 = threading.Thread(target=timed_miner)
    
    t1.start()

    t1.join()
    t2.join()

    print("\n\nDone!")


    
