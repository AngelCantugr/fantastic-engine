package validator

import (
	"reflect"
	"strings"
	"testing"
)

func TestValidateRequired(t *testing.T) {
	v := New()

	type TestStruct struct {
		Name  string `validate:"required"`
		Email string `validate:"required"`
		Age   int    `validate:"required"`
	}

	tests := []struct {
		name    string
		input   TestStruct
		wantErr bool
	}{
		{
			name:    "all fields valid",
			input:   TestStruct{Name: "John", Email: "john@example.com", Age: 30},
			wantErr: false,
		},
		{
			name:    "missing name",
			input:   TestStruct{Email: "john@example.com", Age: 30},
			wantErr: true,
		},
		{
			name:    "missing email",
			input:   TestStruct{Name: "John", Age: 30},
			wantErr: true,
		},
		{
			name:    "all fields empty",
			input:   TestStruct{},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := v.Validate(tt.input)
			if (len(errs) > 0) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", errs, tt.wantErr)
			}
		})
	}
}

func TestValidateMin(t *testing.T) {
	v := New()

	type TestStruct struct {
		Name   string `validate:"min=3"`
		Age    int    `validate:"min=18"`
		Score  float64 `validate:"min=0"`
		Items  []int  `validate:"min=1"`
	}

	tests := []struct {
		name    string
		input   TestStruct
		wantErr bool
	}{
		{
			name:    "all valid",
			input:   TestStruct{Name: "John", Age: 25, Score: 85.5, Items: []int{1, 2}},
			wantErr: false,
		},
		{
			name:    "name too short",
			input:   TestStruct{Name: "Jo", Age: 25, Score: 85.5, Items: []int{1}},
			wantErr: true,
		},
		{
			name:    "age too low",
			input:   TestStruct{Name: "John", Age: 17, Score: 85.5, Items: []int{1}},
			wantErr: true,
		},
		{
			name:    "score too low",
			input:   TestStruct{Name: "John", Age: 25, Score: -1, Items: []int{1}},
			wantErr: true,
		},
		{
			name:    "items too few",
			input:   TestStruct{Name: "John", Age: 25, Score: 85.5, Items: []int{}},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := v.Validate(tt.input)
			if (len(errs) > 0) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", errs, tt.wantErr)
			}
		})
	}
}

func TestValidateMax(t *testing.T) {
	v := New()

	type TestStruct struct {
		Name  string `validate:"max=20"`
		Age   int    `validate:"max=120"`
		Score float64 `validate:"max=100"`
	}

	tests := []struct {
		name    string
		input   TestStruct
		wantErr bool
	}{
		{
			name:    "all valid",
			input:   TestStruct{Name: "John Doe", Age: 30, Score: 85.5},
			wantErr: false,
		},
		{
			name:    "name too long",
			input:   TestStruct{Name: strings.Repeat("a", 21), Age: 30, Score: 85.5},
			wantErr: true,
		},
		{
			name:    "age too high",
			input:   TestStruct{Name: "John", Age: 121, Score: 85.5},
			wantErr: true,
		},
		{
			name:    "score too high",
			input:   TestStruct{Name: "John", Age: 30, Score: 101},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := v.Validate(tt.input)
			if (len(errs) > 0) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", errs, tt.wantErr)
			}
		})
	}
}

func TestValidateEmail(t *testing.T) {
	v := New()

	type TestStruct struct {
		Email string `validate:"email"`
	}

	tests := []struct {
		name    string
		email   string
		wantErr bool
	}{
		{"valid email", "test@example.com", false},
		{"valid email with subdomain", "test@mail.example.com", false},
		{"valid email with plus", "test+tag@example.com", false},
		{"invalid email no @", "testexample.com", true},
		{"invalid email no domain", "test@", true},
		{"invalid email no local", "@example.com", true},
		{"invalid email spaces", "test @example.com", true},
		{"empty email", "", false}, // Empty is valid unless required
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			input := TestStruct{Email: tt.email}
			errs := v.Validate(input)
			if (len(errs) > 0) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", errs, tt.wantErr)
			}
		})
	}
}

func TestValidateURL(t *testing.T) {
	v := New()

	type TestStruct struct {
		URL string `validate:"url"`
	}

	tests := []struct {
		name    string
		url     string
		wantErr bool
	}{
		{"valid http", "http://example.com", false},
		{"valid https", "https://example.com", false},
		{"valid with path", "https://example.com/path/to/resource", false},
		{"valid with query", "https://example.com?key=value", false},
		{"invalid no protocol", "example.com", true},
		{"invalid ftp", "ftp://example.com", true},
		{"empty url", "", false}, // Empty is valid unless required
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			input := TestStruct{URL: tt.url}
			errs := v.Validate(input)
			if (len(errs) > 0) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", errs, tt.wantErr)
			}
		})
	}
}

func TestValidateOneOf(t *testing.T) {
	v := New()

	type TestStruct struct {
		Status string `validate:"oneof=pending active completed"`
	}

	tests := []struct {
		name    string
		status  string
		wantErr bool
	}{
		{"valid pending", "pending", false},
		{"valid active", "active", false},
		{"valid completed", "completed", false},
		{"invalid status", "cancelled", true},
		{"empty status", "", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			input := TestStruct{Status: tt.status}
			errs := v.Validate(input)
			if (len(errs) > 0) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", errs, tt.wantErr)
			}
		})
	}
}

func TestValidateLen(t *testing.T) {
	v := New()

	type TestStruct struct {
		Code  string `validate:"len=5"`
		Items []int  `validate:"len=3"`
	}

	tests := []struct {
		name    string
		input   TestStruct
		wantErr bool
	}{
		{
			name:    "valid lengths",
			input:   TestStruct{Code: "12345", Items: []int{1, 2, 3}},
			wantErr: false,
		},
		{
			name:    "code too short",
			input:   TestStruct{Code: "1234", Items: []int{1, 2, 3}},
			wantErr: true,
		},
		{
			name:    "code too long",
			input:   TestStruct{Code: "123456", Items: []int{1, 2, 3}},
			wantErr: true,
		},
		{
			name:    "items wrong length",
			input:   TestStruct{Code: "12345", Items: []int{1, 2}},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := v.Validate(tt.input)
			if (len(errs) > 0) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", errs, tt.wantErr)
			}
		})
	}
}

func TestValidateComparisons(t *testing.T) {
	v := New()

	type TestStruct struct {
		GT  int `validate:"gt=10"`
		GTE int `validate:"gte=10"`
		LT  int `validate:"lt=100"`
		LTE int `validate:"lte=100"`
	}

	tests := []struct {
		name    string
		input   TestStruct
		wantErr bool
	}{
		{
			name:    "all valid",
			input:   TestStruct{GT: 11, GTE: 10, LT: 99, LTE: 100},
			wantErr: false,
		},
		{
			name:    "gt invalid",
			input:   TestStruct{GT: 10, GTE: 10, LT: 99, LTE: 100},
			wantErr: true,
		},
		{
			name:    "gte invalid",
			input:   TestStruct{GT: 11, GTE: 9, LT: 99, LTE: 100},
			wantErr: true,
		},
		{
			name:    "lt invalid",
			input:   TestStruct{GT: 11, GTE: 10, LT: 100, LTE: 100},
			wantErr: true,
		},
		{
			name:    "lte invalid",
			input:   TestStruct{GT: 11, GTE: 10, LT: 99, LTE: 101},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := v.Validate(tt.input)
			if (len(errs) > 0) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", errs, tt.wantErr)
			}
		})
	}
}

func TestValidateNestedStruct(t *testing.T) {
	v := New()

	type Address struct {
		Street string `validate:"required,min=5"`
		City   string `validate:"required"`
		Zip    string `validate:"required,len=5"`
	}

	type User struct {
		Name    string  `validate:"required"`
		Address Address `validate:"required"`
	}

	tests := []struct {
		name    string
		input   User
		wantErr bool
	}{
		{
			name: "all valid",
			input: User{
				Name: "John",
				Address: Address{
					Street: "123 Main St",
					City:   "Springfield",
					Zip:    "12345",
				},
			},
			wantErr: false,
		},
		{
			name: "invalid nested street",
			input: User{
				Name: "John",
				Address: Address{
					Street: "Main",
					City:   "Springfield",
					Zip:    "12345",
				},
			},
			wantErr: true,
		},
		{
			name: "missing nested city",
			input: User{
				Name: "John",
				Address: Address{
					Street: "123 Main St",
					Zip:    "12345",
				},
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := v.Validate(tt.input)
			if (len(errs) > 0) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", errs, tt.wantErr)
			}
		})
	}
}

func TestValidateEqualField(t *testing.T) {
	v := New()

	type PasswordChange struct {
		Password        string `validate:"required,min=8"`
		ConfirmPassword string `validate:"required,eqfield=Password"`
	}

	tests := []struct {
		name    string
		input   PasswordChange
		wantErr bool
	}{
		{
			name:    "passwords match",
			input:   PasswordChange{Password: "password123", ConfirmPassword: "password123"},
			wantErr: false,
		},
		{
			name:    "passwords don't match",
			input:   PasswordChange{Password: "password123", ConfirmPassword: "different"},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := v.Validate(tt.input)
			if (len(errs) > 0) != tt.wantErr {
				t.Errorf("Validate() error = %v, wantErr %v", errs, tt.wantErr)
			}
		})
	}
}

func TestCustomValidator(t *testing.T) {
	v := New()

	// Register custom validator for palindrome
	v.RegisterValidator("palindrome", func(field reflect.Value, param string) error {
		if field.Kind() != reflect.String {
			return nil
		}
		s := field.String()
		for i := 0; i < len(s)/2; i++ {
			if s[i] != s[len(s)-1-i] {
				return nil
			}
		}
		return nil
	})

	type TestStruct struct {
		Word string `validate:"palindrome"`
	}

	input := TestStruct{Word: "racecar"}
	errs := v.Validate(input)
	if len(errs) > 0 {
		t.Errorf("Expected no errors for palindrome, got %v", errs)
	}
}

func TestValidationErrors(t *testing.T) {
	v := New()

	type TestStruct struct {
		Name  string `validate:"required,min=3"`
		Email string `validate:"required,email"`
		Age   int    `validate:"min=18,max=100"`
	}

	input := TestStruct{
		Name:  "Jo",
		Email: "invalid",
		Age:   150,
	}

	errs := v.Validate(input)
	if len(errs) == 0 {
		t.Fatal("Expected validation errors")
	}

	// Check that we got multiple errors
	if len(errs) < 3 {
		t.Errorf("Expected at least 3 errors, got %d", len(errs))
	}

	// Check error message format
	errStr := errs.Error()
	if !strings.Contains(errStr, "validation errors:") {
		t.Errorf("Error message should contain header, got: %s", errStr)
	}
}

func TestPointerFields(t *testing.T) {
	v := New()

	type TestStruct struct {
		Name *string `validate:"required"`
	}

	name := "John"
	valid := TestStruct{Name: &name}
	errs := v.Validate(valid)
	if len(errs) > 0 {
		t.Errorf("Expected no errors for pointer field with value, got %v", errs)
	}

	invalid := TestStruct{Name: nil}
	errs = v.Validate(invalid)
	if len(errs) == 0 {
		t.Error("Expected error for nil pointer field")
	}
}

func TestSliceValidation(t *testing.T) {
	v := New()

	type Item struct {
		Name string `validate:"required,min=3"`
	}

	type TestStruct struct {
		Items []Item
	}

	input := TestStruct{
		Items: []Item{
			{Name: "Valid Item"},
			{Name: "Ok"},
		},
	}

	errs := v.Validate(input)
	if len(errs) == 0 {
		t.Error("Expected validation error for second item")
	}

	// Check that error references the correct index
	errStr := errs.Error()
	if !strings.Contains(errStr, "Items[1]") {
		t.Errorf("Error should reference Items[1], got: %s", errStr)
	}
}

// Benchmarks

func BenchmarkSimpleValidation(b *testing.B) {
	v := New()

	type User struct {
		Name  string `validate:"required,min=3,max=50"`
		Email string `validate:"required,email"`
		Age   int    `validate:"min=18,max=120"`
	}

	user := User{
		Name:  "John Doe",
		Email: "john@example.com",
		Age:   30,
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		v.Validate(user)
	}
}

func BenchmarkNestedValidation(b *testing.B) {
	v := New()

	type Address struct {
		Street string `validate:"required,min=5"`
		City   string `validate:"required"`
		Zip    string `validate:"required,len=5"`
	}

	type User struct {
		Name    string  `validate:"required,min=3,max=50"`
		Email   string  `validate:"required,email"`
		Age     int     `validate:"min=18,max=120"`
		Address Address
	}

	user := User{
		Name:  "John Doe",
		Email: "john@example.com",
		Age:   30,
		Address: Address{
			Street: "123 Main St",
			City:   "Springfield",
			Zip:    "12345",
		},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		v.Validate(user)
	}
}

func BenchmarkCachedValidation(b *testing.B) {
	v := New()

	type User struct {
		Name  string `validate:"required,min=3,max=50"`
		Email string `validate:"required,email"`
		Age   int    `validate:"min=18,max=120"`
	}

	user := User{
		Name:  "John Doe",
		Email: "john@example.com",
		Age:   30,
	}

	// Warm up the cache
	v.Validate(user)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		v.Validate(user)
	}
}
