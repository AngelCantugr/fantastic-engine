package jit

import (
	"testing"
)

func TestInterpreterBasic(t *testing.T) {
	// Program: 5 + 3 = 8
	program := &Program{
		Instructions: []Instruction{
			{Op: OpPush, Arg: 5},
			{Op: OpPush, Arg: 3},
			{Op: OpAdd},
			{Op: OpRet},
		},
	}

	interp := NewInterpreter()
	result, err := interp.Execute(program)
	if err != nil {
		t.Fatalf("Execution failed: %v", err)
	}

	if result != 8 {
		t.Errorf("Expected 8, got %d", result)
	}
}

func TestInterpreterSubtraction(t *testing.T) {
	// Program: 10 - 3 = 7
	program := &Program{
		Instructions: []Instruction{
			{Op: OpPush, Arg: 10},
			{Op: OpPush, Arg: 3},
			{Op: OpSub},
			{Op: OpRet},
		},
	}

	interp := NewInterpreter()
	result, err := interp.Execute(program)
	if err != nil {
		t.Fatalf("Execution failed: %v", err)
	}

	if result != 7 {
		t.Errorf("Expected 7, got %d", result)
	}
}

func TestInterpreterMultiplication(t *testing.T) {
	// Program: 4 * 5 = 20
	program := &Program{
		Instructions: []Instruction{
			{Op: OpPush, Arg: 4},
			{Op: OpPush, Arg: 5},
			{Op: OpMul},
			{Op: OpRet},
		},
	}

	interp := NewInterpreter()
	result, err := interp.Execute(program)
	if err != nil {
		t.Fatalf("Execution failed: %v", err)
	}

	if result != 20 {
		t.Errorf("Expected 20, got %d", result)
	}
}

func TestInterpreterComplex(t *testing.T) {
	// Program: (5 + 3) * 2 = 16
	program := &Program{
		Instructions: []Instruction{
			{Op: OpPush, Arg: 5},
			{Op: OpPush, Arg: 3},
			{Op: OpAdd},
			{Op: OpPush, Arg: 2},
			{Op: OpMul},
			{Op: OpRet},
		},
	}

	interp := NewInterpreter()
	result, err := interp.Execute(program)
	if err != nil {
		t.Fatalf("Execution failed: %v", err)
	}

	if result != 16 {
		t.Errorf("Expected 16, got %d", result)
	}
}

func TestJITCompilerBasic(t *testing.T) {
	// Program: 5 + 3 = 8
	program := &Program{
		Instructions: []Instruction{
			{Op: OpPush, Arg: 5},
			{Op: OpPush, Arg: 3},
			{Op: OpAdd},
			{Op: OpRet},
		},
	}

	jit := NewJITCompiler()
	if err := jit.Compile(program); err != nil {
		t.Fatalf("Compilation failed: %v", err)
	}
	defer jit.Free()

	result, err := jit.Execute()
	if err != nil {
		t.Fatalf("Execution failed: %v", err)
	}

	if result != 8 {
		t.Errorf("Expected 8, got %d", result)
	}
}

func TestOptimizer(t *testing.T) {
	// Program with constant folding opportunity
	program := &Program{
		Instructions: []Instruction{
			{Op: OpPush, Arg: 5},
			{Op: OpPush, Arg: 3},
			{Op: OpAdd},
			{Op: OpRet},
		},
	}

	optimizer := NewOptimizer()
	optimized := optimizer.Optimize(program)

	if len(optimized.Instructions) >= len(program.Instructions) {
		t.Error("Expected optimization to reduce instruction count")
	}
}

func TestDisassembler(t *testing.T) {
	program := &Program{
		Instructions: []Instruction{
			{Op: OpPush, Arg: 5},
			{Op: OpPush, Arg: 3},
			{Op: OpAdd},
			{Op: OpRet},
		},
	}

	dis := &Disassembler{}
	output := dis.Disassemble(program)

	if output == "" {
		t.Error("Expected non-empty disassembly output")
	}
}

func BenchmarkInterpreter(b *testing.B) {
	program := &Program{
		Instructions: []Instruction{
			{Op: OpPush, Arg: 5},
			{Op: OpPush, Arg: 3},
			{Op: OpAdd},
			{Op: OpRet},
		},
	}

	interp := NewInterpreter()
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		interp.Execute(program)
	}
}

func BenchmarkJIT(b *testing.B) {
	program := &Program{
		Instructions: []Instruction{
			{Op: OpPush, Arg: 5},
			{Op: OpPush, Arg: 3},
			{Op: OpAdd},
			{Op: OpRet},
		},
	}

	jit := NewJITCompiler()
	jit.Compile(program)
	defer jit.Free()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		jit.Execute()
	}
}
