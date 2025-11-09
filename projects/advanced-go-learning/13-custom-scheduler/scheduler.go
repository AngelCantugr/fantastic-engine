package scheduler

import (
	"context"
	"math/rand"
	"sync"
	"sync/atomic"
	"time"
)

type Task struct {
	ID       uint64
	Priority int
	Fn       func()
	ctx      context.Context
}

type WorkQueue struct {
	tasks []*Task
	mu    sync.Mutex
}

func (wq *WorkQueue) Push(task *Task) {
	wq.mu.Lock()
	defer wq.mu.Unlock()
	wq.tasks = append(wq.tasks, task)
}

func (wq *WorkQueue) Pop() *Task {
	wq.mu.Lock()
	defer wq.mu.Unlock()

	if len(wq.tasks) == 0 {
		return nil
	}

	task := wq.tasks[0]
	wq.tasks = wq.tasks[1:]
	return task
}

func (wq *WorkQueue) Steal() *Task {
	wq.mu.Lock()
	defer wq.mu.Unlock()

	if len(wq.tasks) < 2 {
		return nil
	}

	// Steal from the end
	task := wq.tasks[len(wq.tasks)-1]
	wq.tasks = wq.tasks[:len(wq.tasks)-1]
	return task
}

func (wq *WorkQueue) Len() int {
	wq.mu.Lock()
	defer wq.mu.Unlock()
	return len(wq.tasks)
}

type Worker struct {
	id          int
	localQueue  *WorkQueue
	scheduler   *Scheduler
	taskCount   uint64
}

func (w *Worker) run(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return
		default:
			task := w.findTask()
			if task == nil {
				time.Sleep(time.Millisecond)
				continue
			}

			task.Fn()
			atomic.AddUint64(&w.taskCount, 1)
			atomic.AddUint64(&w.scheduler.completedTasks, 1)
		}
	}
}

func (w *Worker) findTask() *Task {
	// Try local queue first
	if task := w.localQueue.Pop(); task != nil {
		return task
	}

	// Try global queue
	if task := w.scheduler.globalQueue.Pop(); task != nil {
		return task
	}

	// Try work stealing from other workers
	return w.steal()
}

func (w *Worker) steal() *Task {
	// Randomly select other workers to steal from
	workers := w.scheduler.workers
	for i := 0; i < len(workers); i++ {
		victimID := rand.Intn(len(workers))
		if victimID == w.id {
			continue
		}

		if task := workers[victimID].localQueue.Steal(); task != nil {
			atomic.AddUint64(&w.scheduler.stolenTasks, 1)
			return task
		}
	}

	return nil
}

type Scheduler struct {
	workers        []*Worker
	globalQueue    *WorkQueue
	ctx            context.Context
	cancel         context.CancelFunc
	taskIDCounter  uint64
	completedTasks uint64
	stolenTasks    uint64
}

func NewScheduler(numWorkers int) *Scheduler {
	ctx, cancel := context.WithCancel(context.Background())

	s := &Scheduler{
		workers:     make([]*Worker, numWorkers),
		globalQueue: &WorkQueue{tasks: make([]*Task, 0)},
		ctx:         ctx,
		cancel:      cancel,
	}

	for i := 0; i < numWorkers; i++ {
		worker := &Worker{
			id:         i,
			localQueue: &WorkQueue{tasks: make([]*Task, 0)},
			scheduler:  s,
		}
		s.workers[i] = worker
		go worker.run(ctx)
	}

	return s
}

func (s *Scheduler) Submit(fn func()) {
	s.SubmitWithPriority(fn, 0)
}

func (s *Scheduler) SubmitWithPriority(fn func(), priority int) {
	task := &Task{
		ID:       atomic.AddUint64(&s.taskIDCounter, 1),
		Priority: priority,
		Fn:       fn,
		ctx:      s.ctx,
	}

	// Try to submit to least loaded worker
	minWorker := s.workers[0]
	minLoad := minWorker.localQueue.Len()

	for _, worker := range s.workers[1:] {
		if load := worker.localQueue.Len(); load < minLoad {
			minWorker = worker
			minLoad = load
		}
	}

	if minLoad < 10 {
		minWorker.localQueue.Push(task)
	} else {
		s.globalQueue.Push(task)
	}
}

func (s *Scheduler) Shutdown() {
	s.cancel()
}

func (s *Scheduler) Stats() map[string]interface{} {
	globalLen := s.globalQueue.Len()
	localTotal := 0

	for _, worker := range s.workers {
		localTotal += worker.localQueue.Len()
	}

	return map[string]interface{}{
		"workers":         len(s.workers),
		"completed_tasks": atomic.LoadUint64(&s.completedTasks),
		"stolen_tasks":    atomic.LoadUint64(&s.stolenTasks),
		"global_queue":    globalLen,
		"local_queues":    localTotal,
	}
}
