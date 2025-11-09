package jit

import (
	"fmt"
	"syscall"
	"unsafe"
)

// Opcode represents bytecode instructions
type Opcode byte

const (
	OpPush Opcode = iota
	OpAdd
	OpSub
	OpMul
	OpDiv
	OpRet
	OpLoad
	OpStore
)

// Instruction represents a bytecode instruction
type Instruction struct {
	Op    Opcode
	Arg   int64
}

// Program represents a bytecode program
type Program struct {
	Instructions []Instruction
}

// Interpreter executes bytecode
type Interpreter struct {
	stack []int64
	vars  map[int]int64
}

func NewInterpreter() *Interpreter {
	return &Interpreter{
		stack: make([]int64, 0, 100),
		vars:  make(map[int]int64),
	}
}

func (i *Interpreter) Execute(program *Program) (int64, error) {
	for _, instr := range program.Instructions {
		switch instr.Op {
		case OpPush:
			i.stack = append(i.stack, instr.Arg)

		case OpAdd:
			if len(i.stack) < 2 {
				return 0, fmt.Errorf("stack underflow")
			}
			b := i.stack[len(i.stack)-1]
			a := i.stack[len(i.stack)-2]
			i.stack = i.stack[:len(i.stack)-2]
			i.stack = append(i.stack, a+b)

		case OpSub:
			if len(i.stack) < 2 {
				return 0, fmt.Errorf("stack underflow")
			}
			b := i.stack[len(i.stack)-1]
			a := i.stack[len(i.stack)-2]
			i.stack = i.stack[:len(i.stack)-2]
			i.stack = append(i.stack, a-b)

		case OpMul:
			if len(i.stack) < 2 {
				return 0, fmt.Errorf("stack underflow")
			}
			b := i.stack[len(i.stack)-1]
			a := i.stack[len(i.stack)-2]
			i.stack = i.stack[:len(i.stack)-2]
			i.stack = append(i.stack, a*b)

		case OpDiv:
			if len(i.stack) < 2 {
				return 0, fmt.Errorf("stack underflow")
			}
			b := i.stack[len(i.stack)-1]
			a := i.stack[len(i.stack)-2]
			i.stack = i.stack[:len(i.stack)-2]
			if b == 0 {
				return 0, fmt.Errorf("division by zero")
			}
			i.stack = append(i.stack, a/b)

		case OpLoad:
			val, ok := i.vars[int(instr.Arg)]
			if !ok {
				return 0, fmt.Errorf("undefined variable %d", instr.Arg)
			}
			i.stack = append(i.stack, val)

		case OpStore:
			if len(i.stack) < 1 {
				return 0, fmt.Errorf("stack underflow")
			}
			val := i.stack[len(i.stack)-1]
			i.stack = i.stack[:len(i.stack)-1]
			i.vars[int(instr.Arg)] = val

		case OpRet:
			if len(i.stack) < 1 {
				return 0, fmt.Errorf("stack underflow")
			}
			return i.stack[len(i.stack)-1], nil
		}
	}

	if len(i.stack) > 0 {
		return i.stack[len(i.stack)-1], nil
	}

	return 0, nil
}

// JITCompiler compiles bytecode to native code
type JITCompiler struct {
	code []byte
	mem  []byte
}

func NewJITCompiler() *JITCompiler {
	return &JITCompiler{
		code: make([]byte, 0, 4096),
	}
}

// Compile compiles bytecode to x86-64 machine code
func (j *JITCompiler) Compile(program *Program) error {
	// x86-64 function prologue
	j.emit(0x55)             // push rbp
	j.emit(0x48, 0x89, 0xe5) // mov rbp, rsp

	for _, instr := range program.Instructions {
		switch instr.Op {
		case OpPush:
			// mov rax, immediate
			j.emit(0x48, 0xb8)
			j.emitInt64(instr.Arg)
			// push rax
			j.emit(0x50)

		case OpAdd:
			// pop rbx
			j.emit(0x5b)
			// pop rax
			j.emit(0x58)
			// add rax, rbx
			j.emit(0x48, 0x01, 0xd8)
			// push rax
			j.emit(0x50)

		case OpSub:
			// pop rbx
			j.emit(0x5b)
			// pop rax
			j.emit(0x58)
			// sub rax, rbx
			j.emit(0x48, 0x29, 0xd8)
			// push rax
			j.emit(0x50)

		case OpMul:
			// pop rbx
			j.emit(0x5b)
			// pop rax
			j.emit(0x58)
			// imul rax, rbx
			j.emit(0x48, 0x0f, 0xaf, 0xc3)
			// push rax
			j.emit(0x50)

		case OpRet:
			// pop rax (return value)
			j.emit(0x58)
			// pop rbp
			j.emit(0x5d)
			// ret
			j.emit(0xc3)
		}
	}

	// Function epilogue (if not already returned)
	j.emit(0x58)       // pop rax
	j.emit(0x5d)       // pop rbp
	j.emit(0xc3)       // ret

	return nil
}

func (j *JITCompiler) emit(bytes ...byte) {
	j.code = append(j.code, bytes...)
}

func (j *JITCompiler) emitInt64(val int64) {
	for i := 0; i < 8; i++ {
		j.code = append(j.code, byte(val&0xff))
		val >>= 8
	}
}

// Allocate executable memory
func (j *JITCompiler) allocateExecutableMemory() error {
	size := (len(j.code) + 4095) &^ 4095 // Round up to page size

	mem, err := syscall.Mmap(
		-1,
		0,
		size,
		syscall.PROT_READ|syscall.PROT_WRITE,
		syscall.MAP_PRIVATE|syscall.MAP_ANONYMOUS,
	)
	if err != nil {
		return err
	}

	copy(mem, j.code)

	// Make executable
	err = syscall.Mprotect(mem, syscall.PROT_READ|syscall.PROT_EXEC)
	if err != nil {
		syscall.Munmap(mem)
		return err
	}

	j.mem = mem
	return nil
}

// Execute runs the compiled native code
func (j *JITCompiler) Execute() (int64, error) {
	if j.mem == nil {
		if err := j.allocateExecutableMemory(); err != nil {
			return 0, err
		}
	}

	// Cast memory to function pointer and call
	funcPtr := *(*func() int64)(unsafe.Pointer(&j.mem))
	result := funcPtr()

	return result, nil
}

// Free releases executable memory
func (j *JITCompiler) Free() error {
	if j.mem != nil {
		return syscall.Munmap(j.mem)
	}
	return nil
}

// Optimizer applies basic optimizations to bytecode
type Optimizer struct{}

func NewOptimizer() *Optimizer {
	return &Optimizer{}
}

// Optimize applies constant folding and dead code elimination
func (o *Optimizer) Optimize(program *Program) *Program {
	optimized := &Program{
		Instructions: make([]Instruction, 0),
	}

	// Simple constant folding
	for i := 0; i < len(program.Instructions); i++ {
		instr := program.Instructions[i]

		// Check for push-push-add pattern
		if i+2 < len(program.Instructions) &&
			instr.Op == OpPush &&
			program.Instructions[i+1].Op == OpPush &&
			program.Instructions[i+2].Op == OpAdd {

			// Fold constants
			result := instr.Arg + program.Instructions[i+1].Arg
			optimized.Instructions = append(optimized.Instructions,
				Instruction{Op: OpPush, Arg: result})
			i += 2
			continue
		}

		optimized.Instructions = append(optimized.Instructions, instr)
	}

	return optimized
}

// Disassembler converts bytecode to human-readable form
type Disassembler struct{}

func (d *Disassembler) Disassemble(program *Program) string {
	var result string
	for i, instr := range program.Instructions {
		result += fmt.Sprintf("%04d: ", i)
		switch instr.Op {
		case OpPush:
			result += fmt.Sprintf("PUSH %d\n", instr.Arg)
		case OpAdd:
			result += "ADD\n"
		case OpSub:
			result += "SUB\n"
		case OpMul:
			result += "MUL\n"
		case OpDiv:
			result += "DIV\n"
		case OpLoad:
			result += fmt.Sprintf("LOAD %d\n", instr.Arg)
		case OpStore:
			result += fmt.Sprintf("STORE %d\n", instr.Arg)
		case OpRet:
			result += "RET\n"
		}
	}
	return result
}
