package dbpool

import (
	"context"
	"database/sql"
	"testing"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

func setupTestDB(t *testing.T) *sql.DB {
	db, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		t.Fatalf("Failed to open test database: %v", err)
	}
	return db
}

func TestPoolGetPut(t *testing.T) {
	db := setupTestDB(t)
	defer db.Close()

	pool := NewPool(db, 5, time.Minute)
	defer pool.Close()

	ctx := context.Background()

	conn, err := pool.Get(ctx)
	if err != nil {
		t.Fatalf("Failed to get connection: %v", err)
	}

	if !conn.inUse {
		t.Error("Connection should be marked as in use")
	}

	pool.Put(conn)

	if conn.inUse {
		t.Error("Connection should not be marked as in use after Put")
	}
}

func TestPoolMaxConnections(t *testing.T) {
	db := setupTestDB(t)
	defer db.Close()

	pool := NewPool(db, 2, time.Minute)
	defer pool.Close()

	ctx := context.Background()

	conn1, err := pool.Get(ctx)
	if err != nil {
		t.Fatalf("Failed to get first connection: %v", err)
	}

	conn2, err := pool.Get(ctx)
	if err != nil {
		t.Fatalf("Failed to get second connection: %v", err)
	}

	_, err = pool.Get(ctx)
	if err != ErrPoolExhausted {
		t.Errorf("Expected ErrPoolExhausted, got %v", err)
	}

	pool.Put(conn1)
	pool.Put(conn2)
}

func TestPoolClose(t *testing.T) {
	db := setupTestDB(t)
	defer db.Close()

	pool := NewPool(db, 5, time.Minute)

	ctx := context.Background()
	_, err := pool.Get(ctx)
	if err != nil {
		t.Fatalf("Failed to get connection: %v", err)
	}

	pool.Close()

	_, err = pool.Get(ctx)
	if err != ErrPoolClosed {
		t.Errorf("Expected ErrPoolClosed, got %v", err)
	}
}

func TestPoolStats(t *testing.T) {
	db := setupTestDB(t)
	defer db.Close()

	pool := NewPool(db, 5, time.Minute)
	defer pool.Close()

	ctx := context.Background()

	conn1, _ := pool.Get(ctx)
	conn2, _ := pool.Get(ctx)

	stats := pool.Stats()

	if stats["total"].(int) != 2 {
		t.Errorf("Expected total 2, got %d", stats["total"])
	}

	if stats["active"].(int) != 2 {
		t.Errorf("Expected active 2, got %d", stats["active"])
	}

	pool.Put(conn1)

	stats = pool.Stats()
	if stats["active"].(int) != 1 {
		t.Errorf("Expected active 1, got %d", stats["active"])
	}

	if stats["idle"].(int) != 1 {
		t.Errorf("Expected idle 1, got %d", stats["idle"])
	}

	pool.Put(conn2)
}

func TestPoolExecute(t *testing.T) {
	db := setupTestDB(t)
	defer db.Close()

	_, err := db.Exec("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
	if err != nil {
		t.Fatalf("Failed to create table: %v", err)
	}

	pool := NewPool(db, 5, time.Minute)
	defer pool.Close()

	ctx := context.Background()

	err = pool.Execute(ctx, func(conn *sql.Conn) error {
		_, err := conn.ExecContext(ctx, "INSERT INTO test (value) VALUES (?)", "test")
		return err
	})

	if err != nil {
		t.Errorf("Execute failed: %v", err)
	}
}
