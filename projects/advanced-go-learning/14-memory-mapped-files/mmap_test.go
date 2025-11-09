package mmap

import (
	"bytes"
	"os"
	"testing"
)

func TestMemoryMappedFile(t *testing.T) {
	path := "/tmp/test_mmap.bin"
	defer os.Remove(path)

	mmf, err := Open(path, 1024)
	if err != nil {
		t.Fatalf("Failed to create mmap file: %v", err)
	}
	defer mmf.Close()

	// Write data
	data := []byte("Hello, Memory Mapped Files!")
	if err := mmf.WriteAt(0, data); err != nil {
		t.Fatalf("Failed to write: %v", err)
	}

	// Read data back
	read, err := mmf.ReadAt(0, len(data))
	if err != nil {
		t.Fatalf("Failed to read: %v", err)
	}

	if !bytes.Equal(read, data) {
		t.Errorf("Data mismatch: expected %s, got %s", data, read)
	}
}

func TestMemoryMappedFileSync(t *testing.T) {
	path := "/tmp/test_mmap_sync.bin"
	defer os.Remove(path)

	mmf, err := Open(path, 1024)
	if err != nil {
		t.Fatalf("Failed to create mmap file: %v", err)
	}

	data := []byte("Test sync")
	mmf.WriteAt(0, data)

	if err := mmf.Sync(); err != nil {
		t.Fatalf("Failed to sync: %v", err)
	}

	mmf.Close()

	// Reopen and verify
	mmf2, err := OpenReadOnly(path)
	if err != nil {
		t.Fatalf("Failed to reopen: %v", err)
	}
	defer mmf2.Close()

	read, err := mmf2.ReadAt(0, len(data))
	if err != nil {
		t.Fatalf("Failed to read: %v", err)
	}

	if !bytes.Equal(read, data) {
		t.Errorf("Data not persisted correctly")
	}
}

func TestMemoryMappedFileResize(t *testing.T) {
	path := "/tmp/test_mmap_resize.bin"
	defer os.Remove(path)

	mmf, err := Open(path, 1024)
	if err != nil {
		t.Fatalf("Failed to create mmap file: %v", err)
	}
	defer mmf.Close()

	if err := mmf.Resize(2048); err != nil {
		t.Fatalf("Failed to resize: %v", err)
	}

	if mmf.Size() != 2048 {
		t.Errorf("Expected size 2048, got %d", mmf.Size())
	}
}

func BenchmarkMemoryMappedWrite(b *testing.B) {
	path := "/tmp/bench_mmap.bin"
	defer os.Remove(path)

	mmf, _ := Open(path, 1024*1024)
	defer mmf.Close()

	data := make([]byte, 1024)
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		mmf.WriteAt(0, data)
	}
}

func BenchmarkStandardFileWrite(b *testing.B) {
	path := "/tmp/bench_file.bin"
	defer os.Remove(path)

	file, _ := os.Create(path)
	defer file.Close()

	data := make([]byte, 1024)
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		file.WriteAt(data, 0)
	}
}
