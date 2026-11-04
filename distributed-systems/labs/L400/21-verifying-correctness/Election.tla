------------------------------ MODULE Election ------------------------------
\* The toy leader election of modelcheck.py as a TLA+ spec (3 nodes, terms up to MaxTerm).
\* TLC (tla2tools.jar v1.7.4, MIT; Java 11+), pending-ci - not run in the authoring sandbox:
\*   java -cp tla2tools.jar tlc2.TLC -config Election.cfg Election.tla        bug: PersistVote = FALSE -> violation
\*   java -cp tla2tools.jar tlc2.TLC -config ElectionFixed.cfg Election.tla   fix: PersistVote = TRUE  -> no error
EXTENDS Naturals, FiniteSets

CONSTANTS Nodes, MaxTerm, PersistVote, None

VARIABLES term, votedFor, role, votes, cast   \* cast: ghost log of every vote, never erased

vars == <<term, votedFor, role, votes, cast>>

Init == /\ term = [n \in Nodes |-> 0]
        /\ votedFor = [n \in Nodes |-> None]
        /\ role = [n \in Nodes |-> "follower"]
        /\ votes = [n \in Nodes |-> {}]
        /\ cast = {}

Timeout(i) == /\ role[i] # "leader"
              /\ term[i] < MaxTerm
              /\ term' = [term EXCEPT ![i] = term[i] + 1]
              /\ votedFor' = [votedFor EXCEPT ![i] = i]
              /\ role' = [role EXCEPT ![i] = "candidate"]
              /\ votes' = [votes EXCEPT ![i] = {i}]
              /\ cast' = cast \cup {<<term[i] + 1, i, i>>}

BecomeLeader(i) == /\ role[i] = "candidate"
                   /\ 2 * Cardinality(votes[i]) > Cardinality(Nodes)
                   /\ role' = [role EXCEPT ![i] = "leader"]
                   /\ UNCHANGED <<term, votedFor, votes, cast>>

\* j grants candidate i its vote (request and reply delivered in one step, as in modelcheck.py)
Vote(j, i) == /\ role[i] = "candidate"
              /\ j # i
              /\ j \notin votes[i]
              /\ term[j] <= term[i]
              /\ LET fresh == term[j] < term[i]
                     jv == IF fresh THEN None ELSE votedFor[j]
                 IN /\ jv \in {None, i}
                    /\ term' = [term EXCEPT ![j] = term[i]]
                    /\ votedFor' = [votedFor EXCEPT ![j] = i]
                    /\ role' = IF fresh THEN [role EXCEPT ![j] = "follower"] ELSE role
                    /\ votes' = [votes EXCEPT ![i] = votes[i] \cup {j}, ![j] = IF fresh THEN {} ELSE votes[j]]
                    /\ cast' = cast \cup {<<term[i], j, i>>}

\* crash + restart: role and votes are volatile; term persists; votedFor persists only if PersistVote
Restart(j) == LET kept == IF PersistVote THEN votedFor[j] ELSE None
              IN /\ <<votedFor[j], role[j], votes[j]>> # <<kept, "follower", {}>>
                 /\ votedFor' = [votedFor EXCEPT ![j] = kept]
                 /\ role' = [role EXCEPT ![j] = "follower"]
                 /\ votes' = [votes EXCEPT ![j] = {}]
                 /\ UNCHANGED <<term, cast>>

Next == \E i \in Nodes : Timeout(i) \/ BecomeLeader(i) \/ Restart(i) \/ \E j \in Nodes : Vote(j, i)

Spec == Init /\ [][Next]_vars

ElectionSafety == \A a, b \in Nodes : (a # b /\ role[a] = "leader" /\ role[b] = "leader") => term[a] # term[b]

VoteOnce == \A x, y \in cast : (x[1] = y[1] /\ x[2] = y[2]) => x[3] = y[3]
=============================================================================
