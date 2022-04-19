import random
import time
import threading
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

def verify_transaction(p,g,x):
    y = pow(g,x,p)
    r = random.randint(0,p-1)
    h = pow(g,r,p)
    b = int.from_bytes(random.randbytes(1),"big")
    s = (r+b*x)%(p-1)
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

        user_list = [x for x in users if x.username == username]
        user = user_list[0]

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
    global election_chain
    global names_list
    if 'user_id' not in session:
        return redirect(url_for('login'))
    error = None
    nameString=None
    if Blockchain.status == 0:
        error = "Voting has not started yet."
    else:
        nameString = []
        for i in range(len(names_list)):
            nameString.append(str(i+1)+") "+names_list[i])
    if request.method == "POST":
        vote = Vote(request.form["vote"])
        if user.balance != 1:
            error = "You have already voted in this election."
        elif vote.check_vote() and verify_transaction(11,2,int(vote.vote)):
            user.balance -=1
            encrypt_data(users)
            election_chain.unconfirmed_votes.append(vote)
            return render_template("voted.html")
        else:
            error = "Invalid Vote String. Please enter a valid vote."
    return render_template("profile.html", error=error,nameString=nameString)


@app.route("/admin_setup", methods=["GET","POST"])
def admin_home():
    global election_chain
    global names_list
    if 'admin' not in session:
        return redirect(url_for('login'))
    error = None
    if request.method == "POST":
        num_candidates = int(request.form['num'])
        names_list = request.form["names"].split(";")
        if request.form["start_button"] == "Start Elections":
            if num_candidates == len(names_list):
                lock.acquire()
                Vote.candidates = num_candidates
                Blockchain.status = 1
                election_chain = Blockchain(names_list)
                lock.release()
                if t2.is_alive():
                    t2.join()
                t2.start()
                #print("Lock released")
                return redirect(url_for("admin_home2"))
            else:
                error = "Candidates Name count unequal to number of Candidates. Please input names separated by ';'"
    return render_template("admin_start.html", error=error)


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


    