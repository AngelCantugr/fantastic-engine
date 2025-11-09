package raft

import (
	"testing"
	"time"
)

func TestNodeInitialization(t *testing.T) {
	peers := []int{1, 2}
	node := NewNode(0, peers)

	if node.state != Follower {
		t.Errorf("Expected initial state Follower, got %v", node.state)
	}

	if node.currentTerm != 0 {
		t.Errorf("Expected initial term 0, got %d", node.currentTerm)
	}

	if node.votedFor != -1 {
		t.Errorf("Expected votedFor -1, got %d", node.votedFor)
	}
}

func TestBecomeCandidate(t *testing.T) {
	peers := []int{1, 2}
	node := NewNode(0, peers)

	node.becomeCandidate()

	if node.state != Candidate {
		t.Errorf("Expected state Candidate, got %v", node.state)
	}
}

func TestBecomeLeader(t *testing.T) {
	peers := []int{1, 2}
	node := NewNode(0, peers)

	node.becomeLeader()

	if node.state != Leader {
		t.Errorf("Expected state Leader, got %v", node.state)
	}
}

func TestHandleAppendEntries(t *testing.T) {
	peers := []int{1, 2}
	node := NewNode(0, peers)

	respCh := make(chan *AppendEntriesResponse, 1)
	req := &AppendEntriesRequest{
		Term:       1,
		LeaderID:   1,
		ResponseCh: respCh,
	}

	node.handleAppendEntries(req)

	select {
	case resp := <-respCh:
		if !resp.Success {
			t.Error("Expected AppendEntries to succeed")
		}
	case <-time.After(time.Second):
		t.Fatal("Timeout waiting for response")
	}
}

func TestHandleRequestVote(t *testing.T) {
	peers := []int{1, 2}
	node := NewNode(0, peers)

	respCh := make(chan *RequestVoteResponse, 1)
	req := &RequestVoteRequest{
		Term:        1,
		CandidateID: 1,
		ResponseCh:  respCh,
	}

	node.handleRequestVote(req)

	select {
	case resp := <-respCh:
		if !resp.VoteGranted {
			t.Error("Expected vote to be granted")
		}
	case <-time.After(time.Second):
		t.Fatal("Timeout waiting for response")
	}
}

func TestTermUpdate(t *testing.T) {
	peers := []int{1, 2}
	node := NewNode(0, peers)

	node.mu.Lock()
	node.currentTerm = 5
	node.mu.Unlock()

	if node.Term() != 5 {
		t.Errorf("Expected term 5, got %d", node.Term())
	}
}

func TestShutdown(t *testing.T) {
	peers := []int{1, 2}
	node := NewNode(0, peers)

	node.Start()
	time.Sleep(100 * time.Millisecond)

	node.Shutdown()
	time.Sleep(100 * time.Millisecond)
}
