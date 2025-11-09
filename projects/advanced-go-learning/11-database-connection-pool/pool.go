package dbpool

import (
	"context"
	"database/sql"
	"errors"
	"sync"
	"time"
)

var (
	ErrPoolClosed     = errors.New("connection pool is closed")
	ErrPoolExhausted  = errors.New("connection pool exhausted")
	ErrInvalidConn    = errors.New("invalid connection")
)

type Connection struct {
	conn      *sql.Conn
	createdAt time.Time
	lastUsed  time.Time
	inUse     bool
}

type Pool struct {
	db               *sql.DB
	connections      []*Connection
	maxConnections   int
	maxIdleTime      time.Duration
	healthCheckQuery string
	mu               sync.Mutex
	closed           bool
}

func NewPool(db *sql.DB, maxConnections int, maxIdleTime time.Duration) *Pool {
	p := &Pool{
		db:               db,
		connections:      make([]*Connection, 0, maxConnections),
		maxConnections:   maxConnections,
		maxIdleTime:      maxIdleTime,
		healthCheckQuery: "SELECT 1",
	}

	go p.cleanup()
	return p
}

func (p *Pool) Get(ctx context.Context) (*Connection, error) {
	p.mu.Lock()
	defer p.mu.Unlock()

	if p.closed {
		return nil, ErrPoolClosed
	}

	// Try to find an idle connection
	for _, conn := range p.connections {
		if !conn.inUse {
			if p.isHealthy(ctx, conn) {
				conn.inUse = true
				conn.lastUsed = time.Now()
				return conn, nil
			}
			// Remove unhealthy connection
			p.removeConnection(conn)
		}
	}

	// Create new connection if under limit
	if len(p.connections) < p.maxConnections {
		conn, err := p.createConnection(ctx)
		if err != nil {
			return nil, err
		}
		return conn, nil
	}

	return nil, ErrPoolExhausted
}

func (p *Pool) Put(conn *Connection) {
	p.mu.Lock()
	defer p.mu.Unlock()

	if p.closed {
		conn.conn.Close()
		return
	}

	conn.inUse = false
	conn.lastUsed = time.Now()
}

func (p *Pool) Close() error {
	p.mu.Lock()
	defer p.mu.Unlock()

	if p.closed {
		return nil
	}

	p.closed = true

	for _, conn := range p.connections {
		conn.conn.Close()
	}

	p.connections = nil
	return nil
}

func (p *Pool) Stats() map[string]interface{} {
	p.mu.Lock()
	defer p.mu.Unlock()

	active := 0
	idle := 0

	for _, conn := range p.connections {
		if conn.inUse {
			active++
		} else {
			idle++
		}
	}

	return map[string]interface{}{
		"total":  len(p.connections),
		"active": active,
		"idle":   idle,
		"max":    p.maxConnections,
	}
}

func (p *Pool) createConnection(ctx context.Context) (*Connection, error) {
	conn, err := p.db.Conn(ctx)
	if err != nil {
		return nil, err
	}

	c := &Connection{
		conn:      conn,
		createdAt: time.Now(),
		lastUsed:  time.Now(),
		inUse:     true,
	}

	p.connections = append(p.connections, c)
	return c, nil
}

func (p *Pool) isHealthy(ctx context.Context, conn *Connection) bool {
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	_, err := conn.conn.ExecContext(ctx, p.healthCheckQuery)
	return err == nil
}

func (p *Pool) removeConnection(conn *Connection) {
	conn.conn.Close()

	for i, c := range p.connections {
		if c == conn {
			p.connections = append(p.connections[:i], p.connections[i+1:]...)
			break
		}
	}
}

func (p *Pool) cleanup() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		p.mu.Lock()

		if p.closed {
			p.mu.Unlock()
			return
		}

		now := time.Now()
		var toRemove []*Connection

		for _, conn := range p.connections {
			if !conn.inUse && now.Sub(conn.lastUsed) > p.maxIdleTime {
				toRemove = append(toRemove, conn)
			}
		}

		for _, conn := range toRemove {
			p.removeConnection(conn)
		}

		p.mu.Unlock()
	}
}

// Execute runs a query using a connection from the pool
func (p *Pool) Execute(ctx context.Context, fn func(*sql.Conn) error) error {
	conn, err := p.Get(ctx)
	if err != nil {
		return err
	}
	defer p.Put(conn)

	return fn(conn.conn)
}
