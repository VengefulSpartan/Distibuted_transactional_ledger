class raftNode:
    def __init__(self,node_id):

        #node identity
        self.node_id= node_id
        self.state = "Follower"
        #Persistent state
        self.current_term= 0
        self.voted_for= None
        self.log=[]
        # Volatile state
        self.commit_index= 0 #the index number in log(append state) till which it is safe to commit
        self.last_applied= 0 #keeps track of the last log you executed

    #--------RPC (remote procedure calls) Endpoints-----
    def request_vote(self,term,last_log_index,candidate_id,last_log_term):
        #1) Check for term hierarchy
        if term > self.current_term:
            self.current_term=term
            self.voted_for=None
            self.state="Follower"
        elif term < self.current_term:
            return self.current_term,False

        #2)check log completeness
        if len(self.log)>0:
            self_last_log_index = len(self.log)-1
            self_last_log_term = self.log[-1].term
        else:
            self_last_log_index = -1
            self_last_log_term = 0
        log_is_ok=False

        if last_log_term > self_last_log_term :
            log_is_ok=True
        elif last_log_term == self_last_log_term and last_log_index >= self_last_log_index :
            log_is_ok=True

        #3)Vote
        if (self.voted_for is None or self.voted_for==candidate_id) and log_is_ok :
            self.voted_for = candidate_id
            self.state="Follower"
            return self.current_term,True
        #default reject
        return self.current_term,False

        """
        invoked by candidates to ask vote
        Arguments:
        :param term:Candidates' term
        :param last_log_index:index of candidate's last log
        :param candidate_id:Candidates' id
        :param last_log_term: term of candidate's last log

        """

    def append_entries(self,term,leader_id,prev_log_index,prev_log_term,entries,leader_commit):
        """
        Invoked by leaders to append entries or send heartbeat signals

        Arguments:
        :param term: Leaders' term
        :param leader_id: Leaders' id
        :param prev_log_index: index of the log previous to the current log to be appended
        :param prev_log_term: term of the log previous to the current log to be appended
        :param entries: Log entries to store
        :param leader_commit: Leaders' commit index
        :return:
        """
        pass