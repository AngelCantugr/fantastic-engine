package compiler

import (
	"bytes"
	"fmt"
	"go/ast"
	"go/parser"
	"go/printer"
	"go/token"
	"strings"
)

// ASTTransformer applies transformations to Go AST
type ASTTransformer struct {
	fset *token.FileSet
}

func NewTransformer() *ASTTransformer {
	return &ASTTransformer{
		fset: token.NewFileSet(),
	}
}

// ParseFile parses Go source code into AST
func (t *ASTTransformer) ParseFile(source string) (*ast.File, error) {
	return parser.ParseFile(t.fset, "", source, parser.ParseComments)
}

// Print converts AST back to Go source code
func (t *ASTTransformer) Print(node ast.Node) (string, error) {
	var buf bytes.Buffer
	err := printer.Fprint(&buf, t.fset, node)
	if err != nil {
		return "", err
	}
	return buf.String(), nil
}

// AddLogging adds logging statements to all function entries
func (t *ASTTransformer) AddLogging(file *ast.File) {
	ast.Inspect(file, func(n ast.Node) bool {
		fn, ok := n.(*ast.FuncDecl)
		if !ok || fn.Body == nil {
			return true
		}

		// Create log statement
		logStmt := &ast.ExprStmt{
			X: &ast.CallExpr{
				Fun: &ast.SelectorExpr{
					X:   ast.NewIdent("log"),
					Sel: ast.NewIdent("Printf"),
				},
				Args: []ast.Expr{
					&ast.BasicLit{
						Kind:  token.STRING,
						Value: fmt.Sprintf(`"Entering function: %s"`, fn.Name.Name),
					},
				},
			},
		}

		// Insert at beginning of function
		fn.Body.List = append([]ast.Stmt{logStmt}, fn.Body.List...)

		return true
	})
}

// RenameIdentifier renames all occurrences of an identifier
func (t *ASTTransformer) RenameIdentifier(file *ast.File, oldName, newName string) {
	ast.Inspect(file, func(n ast.Node) bool {
		ident, ok := n.(*ast.Ident)
		if ok && ident.Name == oldName {
			ident.Name = newName
		}
		return true
	})
}

// FindFunctions returns all function declarations
func (t *ASTTransformer) FindFunctions(file *ast.File) []*ast.FuncDecl {
	var functions []*ast.FuncDecl

	ast.Inspect(file, func(n ast.Node) bool {
		if fn, ok := n.(*ast.FuncDecl); ok {
			functions = append(functions, fn)
		}
		return true
	})

	return functions
}

// CountLines counts lines of code (excluding comments and blank lines)
func (t *ASTTransformer) CountLines(source string) int {
	lines := strings.Split(source, "\n")
	count := 0

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line != "" && !strings.HasPrefix(line, "//") {
			count++
		}
	}

	return count
}

// Analyzer performs static analysis
type Analyzer struct {
	fset *token.FileSet
}

func NewAnalyzer() *Analyzer {
	return &Analyzer{
		fset: token.NewFileSet(),
	}
}

// FindUnusedVariables finds declared but unused variables
func (a *Analyzer) FindUnusedVariables(source string) ([]string, error) {
	file, err := parser.ParseFile(a.fset, "", source, 0)
	if err != nil {
		return nil, err
	}

	declared := make(map[string]bool)
	used := make(map[string]bool)

	// Find all declarations
	ast.Inspect(file, func(n ast.Node) bool {
		switch node := n.(type) {
		case *ast.AssignStmt:
			if node.Tok == token.DEFINE {
				for _, expr := range node.Lhs {
					if ident, ok := expr.(*ast.Ident); ok {
						declared[ident.Name] = true
					}
				}
			}
		case *ast.Ident:
			// Mark as used (simplified)
			if declared[node.Name] {
				used[node.Name] = true
			}
		}
		return true
	})

	var unused []string
	for name := range declared {
		if !used[name] && name != "_" {
			unused = append(unused, name)
		}
	}

	return unused, nil
}

// CodeGenerator generates code from templates
type CodeGenerator struct {
	fset *token.FileSet
}

func NewCodeGenerator() *CodeGenerator {
	return &CodeGenerator{
		fset: token.NewFileSet(),
	}
}

// GenerateStruct generates a struct declaration
func (g *CodeGenerator) GenerateStruct(name string, fields map[string]string) *ast.GenDecl {
	fieldList := &ast.FieldList{
		List: make([]*ast.Field, 0),
	}

	for fieldName, fieldType := range fields {
		field := &ast.Field{
			Names: []*ast.Ident{ast.NewIdent(fieldName)},
			Type:  ast.NewIdent(fieldType),
		}
		fieldList.List = append(fieldList.List, field)
	}

	return &ast.GenDecl{
		Tok: token.TYPE,
		Specs: []ast.Spec{
			&ast.TypeSpec{
				Name: ast.NewIdent(name),
				Type: &ast.StructType{
					Fields: fieldList,
				},
			},
		},
	}
}

// GenerateGetter generates a getter method
func (g *CodeGenerator) GenerateGetter(structName, fieldName, fieldType string) *ast.FuncDecl {
	return &ast.FuncDecl{
		Recv: &ast.FieldList{
			List: []*ast.Field{
				{
					Names: []*ast.Ident{ast.NewIdent("s")},
					Type: &ast.StarExpr{
						X: ast.NewIdent(structName),
					},
				},
			},
		},
		Name: ast.NewIdent("Get" + strings.Title(fieldName)),
		Type: &ast.FuncType{
			Results: &ast.FieldList{
				List: []*ast.Field{
					{
						Type: ast.NewIdent(fieldType),
					},
				},
			},
		},
		Body: &ast.BlockStmt{
			List: []ast.Stmt{
				&ast.ReturnStmt{
					Results: []ast.Expr{
						&ast.SelectorExpr{
							X:   ast.NewIdent("s"),
							Sel: ast.NewIdent(fieldName),
						},
					},
				},
			},
		},
	}
}

// Metrics calculates code metrics
type Metrics struct {
	Lines       int
	Functions   int
	Structs     int
	Interfaces  int
	Complexity  int
}

func CalculateMetrics(source string) (*Metrics, error) {
	fset := token.NewFileSet()
	file, err := parser.ParseFile(fset, "", source, parser.ParseComments)
	if err != nil {
		return nil, err
	}

	metrics := &Metrics{}

	ast.Inspect(file, func(n ast.Node) bool {
		switch n.(type) {
		case *ast.FuncDecl:
			metrics.Functions++
		case *ast.StructType:
			metrics.Structs++
		case *ast.InterfaceType:
			metrics.Interfaces++
		case *ast.IfStmt, *ast.ForStmt, *ast.SwitchStmt:
			metrics.Complexity++
		}
		return true
	})

	metrics.Lines = len(strings.Split(source, "\n"))

	return metrics, nil
}
