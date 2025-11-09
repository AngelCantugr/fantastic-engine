package workerpool

import (
	"context"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

type Job func(context.Context) error

type Worker struct {
	id       int
	jobQueue chan Job
	quit     chan bool
	pool     *Pool
}

func (w *Worker) start(ctx context.Context) {
	go func() {
		for {
			select {
			case <-ctx.Done():
				return
			case <-w.quit:
				return
			case job := <-w.jobQueue:
				w.pool.incrementActive()
				err := job(ctx)
				w.pool.decrementActive()
				if err != nil {
					w.pool.recordError(err)
				} else {
					w.pool.recordSuccess()
				}
			}
		}
	}()
}

type Pool struct {
	workers      []*Worker
	jobQueue     chan Job
	wg           sync.WaitGroup
	ctx          context.Context
	cancel       context.CancelFunc

	// Metrics
	jobsCompleted uint64
	jobsFailed    uint64
	activeWorkers int32
	mu            sync.RWMutex
}

func NewPool(numWorkers, queueSize int) *Pool {
	ctx, cancel := context.WithCancel(context.Background())

	p := &Pool{
		workers:  make([]*Worker, numWorkers),
		jobQueue: make(chan Job, queueSize),
		ctx:      ctx,
		cancel:   cancel,
	}

	for i := 0; i < numWorkers; i++ {
		worker := &Worker{
			id:       i,
			jobQueue: p.jobQueue,
			quit:     make(chan bool),
			pool:     p,
		}
		p.workers[i] = worker
		worker.start(ctx)
	}

	return p
}

func (p *Pool) Submit(job Job) error {
	select {
	case <-p.ctx.Done():
		return fmt.Errorf("pool is closed")
	case p.jobQueue <- job:
		return nil
	case <-time.After(time.Second):
		return fmt.Errorf("job queue full")
	}
}

func (p *Pool) SubmitWithTimeout(job Job, timeout time.Duration) error {
	select {
	case <-p.ctx.Done():
		return fmt.Errorf("pool is closed")
	case p.jobQueue <- job:
		return nil
	case <-time.After(timeout):
		return fmt.Errorf("submit timeout")
	}
}

func (p *Pool) Shutdown(graceful bool) {
	if graceful {
		close(p.jobQueue)
		p.wg.Wait()
	}

	for _, worker := range p.workers {
		worker.quit <- true
	}

	p.cancel()
}

func (p *Pool) Stats() map[string]interface{} {
	p.mu.RLock()
	defer p.mu.RUnlock()

	return map[string]interface{}{
		"completed":     atomic.LoadUint64(&p.jobsCompleted),
		"failed":        atomic.LoadUint64(&p.jobsFailed),
		"active":        atomic.LoadInt32(&p.activeWorkers),
		"queue_length":  len(p.jobQueue),
		"queue_capacity": cap(p.jobQueue),
	}
}

func (p *Pool) incrementActive() {
	atomic.AddInt32(&p.activeWorkers, 1)
}

func (p *Pool) decrementActive() {
	atomic.AddInt32(&p.activeWorkers, -1)
}

func (p *Pool) recordSuccess() {
	atomic.AddUint64(&p.jobsCompleted, 1)
}

func (p *Pool) recordError(err error) {
	atomic.AddUint64(&p.jobsFailed, 1)
}

// PriorityPool supports job prioritization
type PriorityJob struct {
	Job      Job
	Priority int
}

type PriorityPool struct {
	*Pool
	priorityQueue chan PriorityJob
}

func NewPriorityPool(numWorkers int) *PriorityPool {
	pool := NewPool(numWorkers, 1000)
	pp := &PriorityPool{
		Pool:          pool,
		priorityQueue: make(chan PriorityJob, 1000),
	}

	go pp.processPriorityQueue()
	return pp
}

func (pp *PriorityPool) processPriorityQueue() {
	for pj := range pp.priorityQueue {
		pp.Submit(pj.Job)
	}
}

func (pp *PriorityPool) SubmitWithPriority(job Job, priority int) error {
	select {
	case <-pp.ctx.Done():
		return fmt.Errorf("pool is closed")
	case pp.priorityQueue <- PriorityJob{Job: job, Priority: priority}:
		return nil
	}
}
