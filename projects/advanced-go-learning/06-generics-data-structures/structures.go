package generics

import (
	"fmt"
	"golang.org/x/exp/constraints"
)

// Stack is a generic LIFO data structure
type Stack[T any] struct {
	items []T
}

func NewStack[T any]() *Stack[T] {
	return &Stack[T]{items: make([]T, 0)}
}

func (s *Stack[T]) Push(item T) {
	s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
	var zero T
	if len(s.items) == 0 {
		return zero, false
	}
	item := s.items[len(s.items)-1]
	s.items = s.items[:len(s.items)-1]
	return item, true
}

func (s *Stack[T]) Peek() (T, bool) {
	var zero T
	if len(s.items) == 0 {
		return zero, false
	}
	return s.items[len(s.items)-1], true
}

func (s *Stack[T]) Size() int {
	return len(s.items)
}

func (s *Stack[T]) IsEmpty() bool {
	return len(s.items) == 0
}

// Queue is a generic FIFO data structure
type Queue[T any] struct {
	items []T
}

func NewQueue[T any]() *Queue[T] {
	return &Queue[T]{items: make([]T, 0)}
}

func (q *Queue[T]) Enqueue(item T) {
	q.items = append(q.items, item)
}

func (q *Queue[T]) Dequeue() (T, bool) {
	var zero T
	if len(q.items) == 0 {
		return zero, false
	}
	item := q.items[0]
	q.items = q.items[1:]
	return item, true
}

func (q *Queue[T]) Peek() (T, bool) {
	var zero T
	if len(q.items) == 0 {
		return zero, false
	}
	return q.items[0], true
}

func (q *Queue[T]) Size() int {
	return len(q.items)
}

func (q *Queue[T]) IsEmpty() bool {
	return len(q.items) == 0
}

// LinkedListNode represents a node in a linked list
type LinkedListNode[T any] struct {
	Value T
	Next  *LinkedListNode[T]
}

// LinkedList is a generic singly linked list
type LinkedList[T any] struct {
	head *LinkedListNode[T]
	size int
}

func NewLinkedList[T any]() *LinkedList[T] {
	return &LinkedList[T]{}
}

func (l *LinkedList[T]) Add(value T) {
	node := &LinkedListNode[T]{Value: value}
	if l.head == nil {
		l.head = node
	} else {
		current := l.head
		for current.Next != nil {
			current = current.Next
		}
		current.Next = node
	}
	l.size++
}

func (l *LinkedList[T]) Remove(index int) bool {
	if index < 0 || index >= l.size {
		return false
	}
	if index == 0 {
		l.head = l.head.Next
		l.size--
		return true
	}
	current := l.head
	for i := 0; i < index-1; i++ {
		current = current.Next
	}
	current.Next = current.Next.Next
	l.size--
	return true
}

func (l *LinkedList[T]) Get(index int) (T, bool) {
	var zero T
	if index < 0 || index >= l.size {
		return zero, false
	}
	current := l.head
	for i := 0; i < index; i++ {
		current = current.Next
	}
	return current.Value, true
}

func (l *LinkedList[T]) Size() int {
	return l.size
}

// TreeNode represents a node in a binary tree
type TreeNode[T constraints.Ordered] struct {
	Value T
	Left  *TreeNode[T]
	Right *TreeNode[T]
}

// BinarySearchTree is a generic BST
type BinarySearchTree[T constraints.Ordered] struct {
	root *TreeNode[T]
	size int
}

func NewBST[T constraints.Ordered]() *BinarySearchTree[T] {
	return &BinarySearchTree[T]{}
}

func (bst *BinarySearchTree[T]) Insert(value T) {
	bst.root = bst.insert(bst.root, value)
}

func (bst *BinarySearchTree[T]) insert(node *TreeNode[T], value T) *TreeNode[T] {
	if node == nil {
		bst.size++
		return &TreeNode[T]{Value: value}
	}
	if value < node.Value {
		node.Left = bst.insert(node.Left, value)
	} else if value > node.Value {
		node.Right = bst.insert(node.Right, value)
	}
	return node
}

func (bst *BinarySearchTree[T]) Search(value T) bool {
	return bst.search(bst.root, value)
}

func (bst *BinarySearchTree[T]) search(node *TreeNode[T], value T) bool {
	if node == nil {
		return false
	}
	if value == node.Value {
		return true
	}
	if value < node.Value {
		return bst.search(node.Left, value)
	}
	return bst.search(node.Right, value)
}

func (bst *BinarySearchTree[T]) InOrder() []T {
	var result []T
	bst.inOrder(bst.root, &result)
	return result
}

func (bst *BinarySearchTree[T]) inOrder(node *TreeNode[T], result *[]T) {
	if node != nil {
		bst.inOrder(node.Left, result)
		*result = append(*result, node.Value)
		bst.inOrder(node.Right, result)
	}
}

func (bst *BinarySearchTree[T]) Size() int {
	return bst.size
}

// Graph represents a generic graph structure
type Graph[T comparable] struct {
	vertices map[T][]T
}

func NewGraph[T comparable]() *Graph[T] {
	return &Graph[T]{
		vertices: make(map[T][]T),
	}
}

func (g *Graph[T]) AddVertex(vertex T) {
	if _, exists := g.vertices[vertex]; !exists {
		g.vertices[vertex] = make([]T, 0)
	}
}

func (g *Graph[T]) AddEdge(from, to T) {
	g.AddVertex(from)
	g.AddVertex(to)
	g.vertices[from] = append(g.vertices[from], to)
}

func (g *Graph[T]) BFS(start T) []T {
	visited := make(map[T]bool)
	result := make([]T, 0)
	queue := NewQueue[T]()

	queue.Enqueue(start)
	visited[start] = true

	for !queue.IsEmpty() {
		vertex, _ := queue.Dequeue()
		result = append(result, vertex)

		for _, neighbor := range g.vertices[vertex] {
			if !visited[neighbor] {
				visited[neighbor] = true
				queue.Enqueue(neighbor)
			}
		}
	}

	return result
}

func (g *Graph[T]) DFS(start T) []T {
	visited := make(map[T]bool)
	result := make([]T, 0)
	g.dfs(start, visited, &result)
	return result
}

func (g *Graph[T]) dfs(vertex T, visited map[T]bool, result *[]T) {
	visited[vertex] = true
	*result = append(*result, vertex)

	for _, neighbor := range g.vertices[vertex] {
		if !visited[neighbor] {
			g.dfs(neighbor, visited, result)
		}
	}
}

// Generic utility functions

func Map[T, U any](slice []T, fn func(T) U) []U {
	result := make([]U, len(slice))
	for i, v := range slice {
		result[i] = fn(v)
	}
	return result
}

func Filter[T any](slice []T, predicate func(T) bool) []T {
	result := make([]T, 0)
	for _, v := range slice {
		if predicate(v) {
			result = append(result, v)
		}
	}
	return result
}

func Reduce[T, U any](slice []T, init U, fn func(U, T) U) U {
	result := init
	for _, v := range slice {
		result = fn(result, v)
	}
	return result
}

func Contains[T comparable](slice []T, value T) bool {
	for _, v := range slice {
		if v == value {
			return true
		}
	}
	return false
}

func Max[T constraints.Ordered](slice []T) (T, error) {
	var zero T
	if len(slice) == 0 {
		return zero, fmt.Errorf("empty slice")
	}
	max := slice[0]
	for _, v := range slice[1:] {
		if v > max {
			max = v
		}
	}
	return max, nil
}

func Min[T constraints.Ordered](slice []T) (T, error) {
	var zero T
	if len(slice) == 0 {
		return zero, fmt.Errorf("empty slice")
	}
	min := slice[0]
	for _, v := range slice[1:] {
		if v < min {
			min = v
		}
	}
	return min, nil
}

func Reverse[T any](slice []T) []T {
	result := make([]T, len(slice))
	for i, v := range slice {
		result[len(slice)-1-i] = v
	}
	return result
}

func Unique[T comparable](slice []T) []T {
	seen := make(map[T]bool)
	result := make([]T, 0)
	for _, v := range slice {
		if !seen[v] {
			seen[v] = true
			result = append(result, v)
		}
	}
	return result
}
