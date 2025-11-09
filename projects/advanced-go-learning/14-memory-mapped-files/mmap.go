package mmap

import (
	"fmt"
	"os"
	"syscall"
	"unsafe"
)

type MemoryMappedFile struct {
	file   *os.File
	data   []byte
	size   int64
}

func Open(path string, size int64) (*MemoryMappedFile, error) {
	file, err := os.OpenFile(path, os.O_RDWR|os.O_CREATE, 0644)
	if err != nil {
		return nil, err
	}

	// Ensure file has the right size
	if err := file.Truncate(size); err != nil {
		file.Close()
		return nil, err
	}

	// Memory map the file
	data, err := syscall.Mmap(
		int(file.Fd()),
		0,
		int(size),
		syscall.PROT_READ|syscall.PROT_WRITE,
		syscall.MAP_SHARED,
	)
	if err != nil {
		file.Close()
		return nil, err
	}

	return &MemoryMappedFile{
		file: file,
		data: data,
		size: size,
	}, nil
}

func (m *MemoryMappedFile) ReadAt(offset int64, length int) ([]byte, error) {
	if offset < 0 || offset+int64(length) > m.size {
		return nil, fmt.Errorf("read out of bounds")
	}

	return m.data[offset : offset+int64(length)], nil
}

func (m *MemoryMappedFile) WriteAt(offset int64, data []byte) error {
	if offset < 0 || offset+int64(len(data)) > m.size {
		return fmt.Errorf("write out of bounds")
	}

	copy(m.data[offset:], data)
	return nil
}

func (m *MemoryMappedFile) Sync() error {
	_, _, errno := syscall.Syscall(
		syscall.SYS_MSYNC,
		uintptr(unsafe.Pointer(&m.data[0])),
		uintptr(len(m.data)),
		uintptr(syscall.MS_SYNC),
	)

	if errno != 0 {
		return errno
	}

	return nil
}

func (m *MemoryMappedFile) Close() error {
	if err := syscall.Munmap(m.data); err != nil {
		return err
	}

	return m.file.Close()
}

func (m *MemoryMappedFile) Size() int64 {
	return m.size
}

// Resize changes the size of the memory mapped file
func (m *MemoryMappedFile) Resize(newSize int64) error {
	if err := syscall.Munmap(m.data); err != nil {
		return err
	}

	if err := m.file.Truncate(newSize); err != nil {
		return err
	}

	data, err := syscall.Mmap(
		int(m.file.Fd()),
		0,
		int(newSize),
		syscall.PROT_READ|syscall.PROT_WRITE,
		syscall.MAP_SHARED,
	)
	if err != nil {
		return err
	}

	m.data = data
	m.size = newSize
	return nil
}

// ReadOnly opens a file as read-only memory mapped file
func OpenReadOnly(path string) (*MemoryMappedFile, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}

	info, err := file.Stat()
	if err != nil {
		file.Close()
		return nil, err
	}

	size := info.Size()
	if size == 0 {
		return &MemoryMappedFile{
			file: file,
			data: []byte{},
			size: 0,
		}, nil
	}

	data, err := syscall.Mmap(
		int(file.Fd()),
		0,
		int(size),
		syscall.PROT_READ,
		syscall.MAP_SHARED,
	)
	if err != nil {
		file.Close()
		return nil, err
	}

	return &MemoryMappedFile{
		file: file,
		data: data,
		size: size,
	}, nil
}
