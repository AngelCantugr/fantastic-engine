package generics

import (
	"testing"
)

func TestStack(t *testing.T) {
	s := NewStack[int]()

	s.Push(1)
	s.Push(2)
	s.Push(3)

	if s.Size() != 3 {
		t.Errorf("Expected size 3, got %d", s.Size())
	}

	val, ok := s.Pop()
	if !ok || val != 3 {
		t.Errorf("Expected 3, got %d", val)
	}

	val, ok = s.Peek()
	if !ok || val != 2 {
		t.Errorf("Expected 2, got %d", val)
	}

	if s.Size() != 2 {
		t.Errorf("Expected size 2, got %d", s.Size())
	}
}

func TestQueue(t *testing.T) {
	q := NewQueue[string]()

	q.Enqueue("first")
	q.Enqueue("second")
	q.Enqueue("third")

	if q.Size() != 3 {
		t.Errorf("Expected size 3, got %d", q.Size())
	}

	val, ok := q.Dequeue()
	if !ok || val != "first" {
		t.Errorf("Expected 'first', got '%s'", val)
	}

	val, ok = q.Peek()
	if !ok || val != "second" {
		t.Errorf("Expected 'second', got '%s'", val)
	}
}

func TestLinkedList(t *testing.T) {
	l := NewLinkedList[int]()

	l.Add(10)
	l.Add(20)
	l.Add(30)

	if l.Size() != 3 {
		t.Errorf("Expected size 3, got %d", l.Size())
	}

	val, ok := l.Get(1)
	if !ok || val != 20 {
		t.Errorf("Expected 20, got %d", val)
	}

	l.Remove(1)
	if l.Size() != 2 {
		t.Errorf("Expected size 2, got %d", l.Size())
	}

	val, ok = l.Get(1)
	if !ok || val != 30 {
		t.Errorf("Expected 30, got %d", val)
	}
}

func TestBinarySearchTree(t *testing.T) {
	bst := NewBST[int]()

	bst.Insert(5)
	bst.Insert(3)
	bst.Insert(7)
	bst.Insert(1)
	bst.Insert(9)

	if !bst.Search(7) {
		t.Error("Expected to find 7")
	}

	if bst.Search(100) {
		t.Error("Should not find 100")
	}

	inOrder := bst.InOrder()
	expected := []int{1, 3, 5, 7, 9}
	if len(inOrder) != len(expected) {
		t.Errorf("Expected %d elements, got %d", len(expected), len(inOrder))
	}

	for i, v := range inOrder {
		if v != expected[i] {
			t.Errorf("At index %d, expected %d, got %d", i, expected[i], v)
		}
	}
}

func TestGraph(t *testing.T) {
	g := NewGraph[string]()

	g.AddEdge("A", "B")
	g.AddEdge("A", "C")
	g.AddEdge("B", "D")
	g.AddEdge("C", "D")

	bfs := g.BFS("A")
	if len(bfs) != 4 {
		t.Errorf("Expected 4 vertices in BFS, got %d", len(bfs))
	}

	if bfs[0] != "A" {
		t.Errorf("Expected first vertex to be A, got %s", bfs[0])
	}

	dfs := g.DFS("A")
	if len(dfs) != 4 {
		t.Errorf("Expected 4 vertices in DFS, got %d", len(dfs))
	}

	if dfs[0] != "A" {
		t.Errorf("Expected first vertex to be A, got %s", dfs[0])
	}
}

func TestMap(t *testing.T) {
	input := []int{1, 2, 3, 4, 5}
	result := Map(input, func(x int) int { return x * 2 })

	expected := []int{2, 4, 6, 8, 10}
	for i, v := range result {
		if v != expected[i] {
			t.Errorf("At index %d, expected %d, got %d", i, expected[i], v)
		}
	}
}

func TestFilter(t *testing.T) {
	input := []int{1, 2, 3, 4, 5, 6}
	result := Filter(input, func(x int) bool { return x%2 == 0 })

	expected := []int{2, 4, 6}
	if len(result) != len(expected) {
		t.Errorf("Expected %d elements, got %d", len(expected), len(result))
	}

	for i, v := range result {
		if v != expected[i] {
			t.Errorf("At index %d, expected %d, got %d", i, expected[i], v)
		}
	}
}

func TestReduce(t *testing.T) {
	input := []int{1, 2, 3, 4, 5}
	sum := Reduce(input, 0, func(acc, x int) int { return acc + x })

	if sum != 15 {
		t.Errorf("Expected sum 15, got %d", sum)
	}
}

func TestMax(t *testing.T) {
	input := []int{3, 1, 4, 1, 5, 9, 2, 6}
	max, err := Max(input)

	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}

	if max != 9 {
		t.Errorf("Expected max 9, got %d", max)
	}
}

func TestMin(t *testing.T) {
	input := []int{3, 1, 4, 1, 5, 9, 2, 6}
	min, err := Min(input)

	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}

	if min != 1 {
		t.Errorf("Expected min 1, got %d", min)
	}
}

func TestReverse(t *testing.T) {
	input := []int{1, 2, 3, 4, 5}
	result := Reverse(input)

	expected := []int{5, 4, 3, 2, 1}
	for i, v := range result {
		if v != expected[i] {
			t.Errorf("At index %d, expected %d, got %d", i, expected[i], v)
		}
	}
}

func TestUnique(t *testing.T) {
	input := []int{1, 2, 2, 3, 3, 3, 4, 5, 5}
	result := Unique(input)

	expected := []int{1, 2, 3, 4, 5}
	if len(result) != len(expected) {
		t.Errorf("Expected %d unique elements, got %d", len(expected), len(result))
	}
}

func BenchmarkStackPush(b *testing.B) {
	s := NewStack[int]()
	for i := 0; i < b.N; i++ {
		s.Push(i)
	}
}

func BenchmarkQueueEnqueue(b *testing.B) {
	q := NewQueue[int]()
	for i := 0; i < b.N; i++ {
		q.Enqueue(i)
	}
}

func BenchmarkBSTInsert(b *testing.B) {
	bst := NewBST[int]()
	for i := 0; i < b.N; i++ {
		bst.Insert(i)
	}
}
