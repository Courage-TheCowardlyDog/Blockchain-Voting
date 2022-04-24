from datetime import datetime

class Vote(object):
    candidates = 2 #set number of candidates
    def __init__(self, vote):
        self.vote = vote
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return "<Vote String: %s  Voting Time: %s>" % (self.vote, self.timestamp)

    def check_vote(self):
        sum=0
        if len(self.vote) != Vote.candidates:
            return False
        for i in range(Vote.candidates):
            if int(self.vote[i]) not in [0,1]:
                return False
            else:
                sum+=int(self.vote[i])
        if sum!=1:
            return False
        return True
