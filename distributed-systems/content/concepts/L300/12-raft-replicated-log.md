## Why it matters
A configuration store or lock service must survive a dead machine and never forget a confirmed write. Copying data to three servers is easy; agreeing on one order of writes while servers crash is hard. Raft does this inside etcd, and through etcd inside Kubernetes.

## Mental model
One leader per term keeps the log; followers copy it; an entry counts as committed once a majority stores it. Terms are a logical clock: the higher one wins.

```
term 1:  n1 (leader) [x=1 x=2 x=3]  --AppendEntries-->  n2 [x=1 x=2 x=3]   n3 [x=1 x=2 x=3]
         majority (2 of 3) stores index 3  ->  commit index 3
n1 crashes -> n2, n3 time out -> new term -> one of them wins with 2 of 3 votes
```

## How it works
1. **Elections.** A follower that hears no leader for its randomized timeout increments its term, votes for itself and asks the others. One vote per term; a majority of the full cluster wins. → see lab step 1
2. **Replication.** The leader appends a client command with its term and sends AppendEntries with the index and term of the entry just before the new ones. A follower lacking it refuses; the leader steps back until the logs match, then the follower drops conflicting entries and copies the rest. → see lab step 2
3. **Commit index.** The leader commits index N once a majority holds it and the entry is from the leader's own term; followers learn the commit index from the next AppendEntries. → see lab step 2
4. **Crash and re-election.** Without heartbeats, followers start an election. If two time out together the vote splits and new random timeouts break the tie. → see lab step 3
5. **Election restriction.** A voter refuses a candidate whose log is less up-to-date: later last term wins; equal last terms, the longer log wins. A committed entry sits on a majority and a winner needs a majority, so the winner has it. → see lab steps 4 and 6

Worked example (lab output, seed 7): x=1 and x=2 commit on n1 and n2 while n3 is down; n1 crashes; n3 returns empty and times out first. Without the check, n2 votes for n3 (term 2 is newer), n3 writes x=9 at index 1 and the checker reports three lost committed entries. With the check, n2 answers "candidate log (0, 0) < mine (1, 2)", wins term 3 with n3's vote, and x=9 lands at index 3.

## Failure modes
- **Lost committed writes** after a stale node wins. Only a safety checker or a client re-reading old writes notices; it appeared in 11 of 20 seeds, so happy-path tests miss it.
- **No progress without a majority:** the leader keeps appending but the commit index never moves (tryIt 1). Clients see timeouts, not errors.
- **Disruptive rejoin:** a returning node with a high term forces an election it cannot win (etcd's raft library has PreVote and CheckQuorum for this).
- **Repeated split votes** when timeouts are not random enough.

## Common mistakes
- Granting votes by term alone and forgetting the candidate's log.
- Counting replicas to commit an entry from an earlier term instead of committing through a current-term entry.
- Answering the client when the entry is appended, not committed.
