import time
import random
import math

class LogEntry:
    def __init__(self,term,command):
        self.term=term
        self.command=command

class raftNode:
    def __init__(self,node_id):

        #node identity
        self.node_id= node_id
        self.state = "Follower"
        self.transport=None
        #Persistent state
        self.current_term= 0
        self.voted_for= None
        self.log=[]
        # Volatile state
        self.commit_index= 0 #the index number in log(append state) till which it is safe to commit
        self.last_applied= 0 #keeps track of the last log you executed

        #random timeout to avoid split votes
        self.election_timeout=random.uniform(2.0,4.0)
        #timestamp of last time we heard from the current leader
        self.last_heartbeat=time.time()
        #knowing the neighboring nodes
        self.peers=[]
        self.votes_received=0

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
        #authenticate leader
        if  term < self.current_term :
            return self.current_term,False
        elif term >= self.current_term:
            self.state="Follower"
            self.current_term=term
            #reseting the heartbeat time
            self.last_heartbeat=time.time()


        #Check Log Consistency
        if prev_log_index > len(self.log)-1:
            return self.current_term,False #means you are lagging behind

       #checking term consistency
        if prev_log_index != -1:
            existing_term= self.log[prev_log_index].term
            if existing_term !=prev_log_term:
                return self.current_term,False

        #----------------APPEND LOGIC-----------------
        insert_index=prev_log_index+1

        for entry in entries:

            if len(self.log)>insert_index:#there exists entry at and beyond the current index to be appended
                if self.log[insert_index].term != entry.term:
                    self.log = self.log[:insert_index]  # truncate the log to delete all the wrong entries to the log
                    self.log.append(entry)
            else:
                    self.log.append(entry)
            insert_index+=1

        #-----------------------UPDATE COMMIT INDEX----------------------
        if leader_commit > self.commit_index:
            last_new_index= len(self.log)-1
            self.commit_index= min(leader_commit,last_new_index)

        return self.current_term,True



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
    def set_transport(self,transport):
        self.transport=transport
    def handle_message(self,message,sender_address):
        msg_type=message.get("type").upper()
        if msg_type=="REQUEST_VOTE":
            term=message.get("term")
            candidate_id=message.get("candidate_id")
            last_log_index=message.get("last_log_index")
            last_log_term=message.get("last_log_term")
            term_out,vote= self.request_vote(term,last_log_index,candidate_id,last_log_term)
            response={
                "type":"REQUEST_VOTE_REPLY",
                "term":term_out,
                "vote_granted":vote,
            }
            self.transport.send_message(sender_address,response)
        elif msg_type=="APPEND_ENTRIES":
            #term,leader_id,prev_log_index,prev_log_term,entries,leader_commit
            term=message.get("term")
            leader_id=message.get("leader_id")
            prev_log_index=message.get("prev_log_index")
            prev_log_term=message.get("prev_log_term")
            entries=message.get("entries")
            leader_commit=message.get("leader_commit")

            #converting the entries dictionary

            converted_entries=[]
            for entry in entries:
                entry_term=entry["term"]
                command=entry["command"]
                entry_object=LogEntry(entry_term,command)
                converted_entries.append(entry_object)
            term_out,append=self.append_entries(term,leader_id,prev_log_index,prev_log_term,converted_entries,leader_commit)
            response={
                "type":"APPEND_ENTRIES_REPLY",
                "term":term_out,
                "append_result":append
            }
            self.transport.send_message(sender_address,response)
        elif msg_type=="REQUEST_VOTE_REPLY":
            term=message.get("term")
            vote_granted=message.get("vote_granted")
            #check if we are outdated
            if term>self.current_term:
                self.current_term=term
                self.state="Follower"
                self.voted_for=None
                return
            if self.state == "Candidate" and term==self.current_term and vote_granted :
                self.votes_received+=1
                print(f"Candidate {self.node_id} received Total {self.votes_received} number of votes")
                #majority check
                majority=(len(self.peers)+1)//2 +1
                if self.votes_received>= majority:
                    print(f"Candidate {self.node_id} has got majority of the votes and is Now the LEADER for the term {self.current_term}")
                    self.state="Leader"
                    import threading
                    t=threading.Thread(target=self.start_heartbeat,daemon=True)
                    t.start()




    def run_election_timer(self):
        print(f"node {self.node_id}starting election timer...")
        while True:
            current_time = time.time()
            last_heartbeat = self.last_heartbeat
            time_elapsed = current_time - last_heartbeat

            if self.state == "Leader":
                pass
            elif self.state != "Leader" and time_elapsed>self.election_timeout:
                #panic & start election
                print(f"node {self.node_id} is starting an election !")
                self.start_election()
                #reset timer
                self.last_heartbeat=time.time()
                self.election_timeout=random.uniform(2.0,4.0)

            time.sleep(0.1)#sleeping a little to save CPU power

    def start_heartbeat(self):
        print(f"node {self.node_id} is the LEADER! starting heartbeat ...")
        while self.state == "Leader":
            #heartbeat message
            if len(self.log)>0:
                prev_log_index=len(self.log)-1
                prev_log_term=self.log[-1].term
            else:
                prev_log_index=-1
                prev_log_term=0
            message={
                "type":"APPEND_ENTRIES",
                "term":self.current_term,
                "leader_id":self.node_id,
                "prev_log_index":prev_log_index,
                "prev_log_term":prev_log_term,
                "entries":[],
                "leader_commit":self.commit_index
            }
            for peer in self.peers:
                self.transport.send_message(peer,message)
            time.sleep(0.5)
    def start_election(self):
        self.state="Candidate"
        self.current_term+=1
        self.voted_for=self.node_id
        self.votes_received=1
        self.last_heartbeat=time.time()
        self.election_timeout=random.uniform(2.0,4.0)

        #gather last log info
        if len(self.log)>0:
            last_log_index=len(self.log)-1
            last_log_term=self.log[-1].term
        else:
            last_log_index=-1
            last_log_term=0

        #creating the message
        message={
            "type":"REQUEST_VOTE",
            "term":self.current_term,
            "candidate_id":self.node_id,
            "last_log_index":last_log_index,
            "last_log_term":last_log_term,
        }
        #broadcast it all peers
        print(f"node {self.node_id} sending vote request to all {len(self.peers)}peers...")

        for peer in self.peers:
            self.transport.send_message(peer,message)
