Electronic Voting System Using Blockchain

1) Run user_data.py
        Prepares the Voter's list for the elections. Currently, a mini database has been hardcoded for testing purposes.
2) Run main.py
        initiates two threads:
            a) Flask Webapp that can be accessed using the local IP in the terminal.
            b) Block Miner that mines a block every 30 seconds.

3) Go to http://127.0.0.1:5000/
        (or check where the app is hosted in the terminal)

4) Admin login: (Username: admin | Password: admin)
        Admin is required to enter the candidates' names in order to start the elections.
        Once elections have started, Admin can:
            a) Mine a new block at any instant
            b) Display Blockchain
            c) Display list of eligible voters
            d) Stop elections:
                    This action displays the final blockchain, and also declares the result by adding the votes on the blockchain.

5) User Login: (Username: Naman | Password: secret) (Other login credentials can be viewed in the user_data.py)
        User can only vote once, and if the elections have already started.
        Vote string is in the form of a binary string of length equal to number of candidates, 
        with 0 representing vote not casted for the candidate and 1 representing vote casted for the candidate.
        Example:                                  Correct Voting String
            a) if we have 3 candidates (A,B,C)     -     010       - would mean 1 vote to candidate B
            b) if we have 2 candidates (P,Q)       -     01        - would mean 1 vote to candidate Q
            3) if we have 5 candidates (V,W,X,Y,Z) -     01000     - would mean 1 vote to candidate W

6) Admin Login:
        End elections once the voting is done.


Note: Currently, the user data is visible in "user_data.py" because it has been hardcoded. The blockchain accesses 
and stores the user data in "UserData.pkl.aes" which is an AES encrypted file to prevent manipulation of data. 
