package raft

import (
	"math/rand"
	"sync"
	"sync/atomic"
	"time"
)

// NodeState represents the state of a Raft node
type NodeState int

const (
	Follower NodeState = iota
	Candidate
	Leader
)

// LogEntry represents a log entry
type LogEntry struct {
	Term    int
	Command interface{}
}

// Node represents a Raft node
type Node struct {
	id    int
	state NodeState
	mu    sync.RWMutex

	// Persistent state
	currentTerm int
	votedFor    int
	log         []LogEntry

	// Volatile state
	commitIndex int
	lastApplied int

	// Leader state
	nextIndex  map[int]int
	matchIndex map[int]int

	// Channels
	appendEntriesCh chan *AppendEntriesRequest
	requestVoteCh   chan *RequestVoteRequest
	shutdownCh      chan struct{}

	// Cluster
	peers       []int
	voteCount   int32

	// Timing
	electionTimeout  time.Duration
	heartbeatTimeout time.Duration
	lastHeartbeat    time.Time
}

// AppendEntriesRequest represents an AppendEntries RPC request
type AppendEntriesRequest struct {
	Term         int
	LeaderID     int
	PrevLogIndex int
	PrevLogTerm  int
	Entries      []LogEntry
	LeaderCommit int
	ResponseCh   chan *AppendEntriesResponse
}

// AppendEntriesResponse represents an AppendEntries RPC response
type AppendEntriesResponse struct {
	Term    int
	Success bool
}

// RequestVoteRequest represents a RequestVote RPC request
type RequestVoteRequest struct {
	Term         int
	CandidateID  int
	LastLogIndex int
	LastLogTerm  int
	ResponseCh   chan *RequestVoteResponse
}

// RequestVoteResponse represents a RequestVote RPC response
type RequestVoteResponse struct {
	Term        int
	VoteGranted bool
}

func NewNode(id int, peers []int) *Node {
	return &Node{
		id:               id,
		state:            Follower,
		currentTerm:      0,
		votedFor:         -1,
		log:              make([]LogEntry, 0),
		commitIndex:      0,
		lastApplied:      0,
		nextIndex:        make(map[int]int),
		matchIndex:       make(map[int]int),
		appendEntriesCh:  make(chan *AppendEntriesRequest, 100),
		requestVoteCh:    make(chan *RequestVoteRequest, 100),
		shutdownCh:       make(chan struct{}),
		peers:            peers,
		electionTimeout:  time.Duration(150+rand.Intn(150)) * time.Millisecond,
		heartbeatTimeout: 50 * time.Millisecond,
		lastHeartbeat:    time.Now(),
	}
}

func (n *Node) Start() {
	go n.run()
}

func (n *Node) run() {
	for {
		select {
		case <-n.shutdownCh:
			return
		default:
			n.mu.RLock()
			state := n.state
			n.mu.RUnlock()

			switch state {
			case Follower:
				n.runFollower()
			case Candidate:
				n.runCandidate()
			case Leader:
				n.runLeader()
			}
		}
	}
}

func (n *Node) runFollower() {
	timer := time.NewTimer(n.electionTimeout)
	defer timer.Stop()

	for {
		select {
		case <-n.shutdownCh:
			return
		case <-timer.C:
			// Election timeout - become candidate
			n.becomeCandidate()
			return
		case req := <-n.appendEntriesCh:
			n.handleAppendEntries(req)
			timer.Reset(n.electionTimeout)
		case req := <-n.requestVoteCh:
			n.handleRequestVote(req)
		}
	}
}

func (n *Node) runCandidate() {
	n.mu.Lock()
	n.currentTerm++
	n.votedFor = n.id
	atomic.StoreInt32(&n.voteCount, 1)
	term := n.currentTerm
	n.mu.Unlock()

	// Request votes from peers
	for _, peerID := range n.peers {
		go n.requestVote(peerID, term)
	}

	timer := time.NewTimer(n.electionTimeout)
	defer timer.Stop()

	for {
		select {
		case <-n.shutdownCh:
			return
		case <-timer.C:
			// Election timeout - start new election
			return
		case req := <-n.appendEntriesCh:
			n.handleAppendEntries(req)
			if req.Term >= term {
				n.becomeFollower(req.Term)
				return
			}
		case req := <-n.requestVoteCh:
			n.handleRequestVote(req)
		default:
			votes := atomic.LoadInt32(&n.voteCount)
			if int(votes) > len(n.peers)/2 {
				n.becomeLeader()
				return
			}
		}
	}
}

func (n *Node) runLeader() {
	// Initialize leader state
	n.mu.Lock()
	for _, peerID := range n.peers {
		n.nextIndex[peerID] = len(n.log)
		n.matchIndex[peerID] = 0
	}
	n.mu.Unlock()

	ticker := time.NewTicker(n.heartbeatTimeout)
	defer ticker.Stop()

	for {
		select {
		case <-n.shutdownCh:
			return
		case <-ticker.C:
			n.sendHeartbeats()
		case req := <-n.appendEntriesCh:
			n.handleAppendEntries(req)
		case req := <-n.requestVoteCh:
			n.handleRequestVote(req)
		}
	}
}

func (n *Node) becomeFollower(term int) {
	n.mu.Lock()
	defer n.mu.Unlock()

	n.state = Follower
	n.currentTerm = term
	n.votedFor = -1
}

func (n *Node) becomeCandidate() {
	n.mu.Lock()
	defer n.mu.Unlock()

	n.state = Candidate
}

func (n *Node) becomeLeader() {
	n.mu.Lock()
	defer n.mu.Unlock()

	n.state = Leader
}

func (n *Node) handleAppendEntries(req *AppendEntriesRequest) {
	n.mu.Lock()
	defer n.mu.Unlock()

	resp := &AppendEntriesResponse{
		Term:    n.currentTerm,
		Success: false,
	}

	// Reply false if term < currentTerm
	if req.Term < n.currentTerm {
		req.ResponseCh <- resp
		return
	}

	// Update term if necessary
	if req.Term > n.currentTerm {
		n.currentTerm = req.Term
		n.votedFor = -1
		if n.state != Follower {
			n.state = Follower
		}
	}

	n.lastHeartbeat = time.Now()
	resp.Success = true
	req.ResponseCh <- resp
}

func (n *Node) handleRequestVote(req *RequestVoteRequest) {
	n.mu.Lock()
	defer n.mu.Unlock()

	resp := &RequestVoteResponse{
		Term:        n.currentTerm,
		VoteGranted: false,
	}

	// Reply false if term < currentTerm
	if req.Term < n.currentTerm {
		req.ResponseCh <- resp
		return
	}

	// Update term if necessary
	if req.Term > n.currentTerm {
		n.currentTerm = req.Term
		n.votedFor = -1
	}

	// Grant vote if haven't voted or voted for this candidate
	if n.votedFor == -1 || n.votedFor == req.CandidateID {
		n.votedFor = req.CandidateID
		resp.VoteGranted = true
	}

	req.ResponseCh <- resp
}

func (n *Node) requestVote(peerID int, term int) {
	// Simplified - in real implementation would send RPC
	// This is a placeholder for the voting mechanism
}

func (n *Node) sendHeartbeats() {
	n.mu.RLock()
	term := n.currentTerm
	n.mu.RUnlock()

	for _, peerID := range n.peers {
		go n.sendAppendEntries(peerID, term)
	}
}

func (n *Node) sendAppendEntries(peerID int, term int) {
	// Simplified - in real implementation would send RPC
}

func (n *Node) Shutdown() {
	close(n.shutdownCh)
}

func (n *Node) State() NodeState {
	n.mu.RLock()
	defer n.mu.RUnlock()
	return n.state
}

func (n *Node) Term() int {
	n.mu.RLock()
	defer n.mu.RUnlock()
	return n.currentTerm
}
