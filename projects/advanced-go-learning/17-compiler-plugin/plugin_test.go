package compiler

import (
	"strings"
	"testing"
)

func TestParseFile(t *testing.T) {
	transformer := NewTransformer()

	source := `package main

func main() {
	println("Hello, World!")
}`

	file, err := transformer.ParseFile(source)
	if err != nil {
		t.Fatalf("Failed to parse: %v", err)
	}

	if file.Name.Name != "main" {
		t.Errorf("Expected package name 'main', got '%s'", file.Name.Name)
	}
}

func TestFindFunctions(t *testing.T) {
	transformer := NewTransformer()

	source := `package main

func foo() {}
func bar() {}
func baz() {}`

	file, err := transformer.ParseFile(source)
	if err != nil {
		t.Fatalf("Failed to parse: %v", err)
	}

	functions := transformer.FindFunctions(file)
	if len(functions) != 3 {
		t.Errorf("Expected 3 functions, got %d", len(functions))
	}
}

func TestRenameIdentifier(t *testing.T) {
	transformer := NewTransformer()

	source := `package main

func oldName() {
	x := oldName
}`

	file, err := transformer.ParseFile(source)
	if err != nil {
		t.Fatalf("Failed to parse: %v", err)
	}

	transformer.RenameIdentifier(file, "oldName", "newName")

	output, err := transformer.Print(file)
	if err != nil {
		t.Fatalf("Failed to print: %v", err)
	}

	if !strings.Contains(output, "newName") {
		t.Error("Expected 'newName' in output")
	}

	if strings.Contains(output, "oldName") {
		t.Error("Should not contain 'oldName' in output")
	}
}

func TestGenerateStruct(t *testing.T) {
	gen := NewCodeGenerator()

	fields := map[string]string{
		"Name": "string",
		"Age":  "int",
	}

	structDecl := gen.GenerateStruct("Person", fields)

	if structDecl == nil {
		t.Fatal("Failed to generate struct")
	}
}

func TestCalculateMetrics(t *testing.T) {
	source := `package main

type Person struct {
	Name string
	Age  int
}

func (p *Person) GetName() string {
	return p.Name
}

func main() {
	if true {
		for i := 0; i < 10; i++ {
			println(i)
		}
	}
}`

	metrics, err := CalculateMetrics(source)
	if err != nil {
		t.Fatalf("Failed to calculate metrics: %v", err)
	}

	if metrics.Functions != 2 {
		t.Errorf("Expected 2 functions, got %d", metrics.Functions)
	}

	if metrics.Structs != 1 {
		t.Errorf("Expected 1 struct, got %d", metrics.Structs)
	}

	if metrics.Complexity < 2 {
		t.Errorf("Expected complexity >= 2, got %d", metrics.Complexity)
	}
}

func TestCountLines(t *testing.T) {
	transformer := NewTransformer()

	source := `package main

// Comment
func main() {
	println("test")
}
`

	lines := transformer.CountLines(source)
	if lines < 3 {
		t.Errorf("Expected at least 3 lines, got %d", lines)
	}
}
