package validator

import (
	"fmt"
	"reflect"
	"regexp"
	"strconv"
	"strings"
)

// ValidatorFunc is a function that validates a field value
type ValidatorFunc func(field reflect.Value, param string) error

// Validator holds validation rules and custom validators
type Validator struct {
	validators map[string]ValidatorFunc
	tagCache   map[reflect.Type][]fieldValidation
}

// fieldValidation represents validation rules for a single field
type fieldValidation struct {
	index int
	name  string
	rules []validationRule
}

// validationRule represents a single validation rule
type validationRule struct {
	name  string
	param string
}

// ValidationError represents a validation error for a field
type ValidationError struct {
	Field   string
	Message string
}

// ValidationErrors is a collection of validation errors
type ValidationErrors []ValidationError

func (ve ValidationErrors) Error() string {
	if len(ve) == 0 {
		return ""
	}
	var sb strings.Builder
	sb.WriteString("validation errors:\n")
	for _, err := range ve {
		sb.WriteString(fmt.Sprintf("  - %s: %s\n", err.Field, err.Message))
	}
	return sb.String()
}

// New creates a new Validator with built-in validation rules
func New() *Validator {
	v := &Validator{
		validators: make(map[string]ValidatorFunc),
		tagCache:   make(map[reflect.Type][]fieldValidation),
	}

	// Register built-in validators
	v.RegisterValidator("required", validateRequired)
	v.RegisterValidator("min", validateMin)
	v.RegisterValidator("max", validateMax)
	v.RegisterValidator("len", validateLen)
	v.RegisterValidator("email", validateEmail)
	v.RegisterValidator("url", validateURL)
	v.RegisterValidator("oneof", validateOneOf)
	v.RegisterValidator("gt", validateGreaterThan)
	v.RegisterValidator("gte", validateGreaterThanEqual)
	v.RegisterValidator("lt", validateLessThan)
	v.RegisterValidator("lte", validateLessThanEqual)
	v.RegisterValidator("eqfield", validateEqualField)

	return v
}

// RegisterValidator registers a custom validator function
func (v *Validator) RegisterValidator(name string, fn ValidatorFunc) {
	v.validators[name] = fn
}

// Validate validates a struct and returns any validation errors
func (v *Validator) Validate(s interface{}) ValidationErrors {
	return v.validate(reflect.ValueOf(s), "")
}

// validate is the internal recursive validation function
func (v *Validator) validate(val reflect.Value, prefix string) ValidationErrors {
	// Handle pointers
	if val.Kind() == reflect.Ptr {
		if val.IsNil() {
			return ValidationErrors{{
				Field:   prefix,
				Message: "cannot validate nil pointer",
			}}
		}
		val = val.Elem()
	}

	// Only validate structs
	if val.Kind() != reflect.Struct {
		return nil
	}

	var errors ValidationErrors
	typ := val.Type()

	// Get or create cached field validations
	fieldValidations := v.getFieldValidations(typ)

	// Validate each field
	for _, fv := range fieldValidations {
		field := val.Field(fv.index)
		fieldName := fv.name
		if prefix != "" {
			fieldName = prefix + "." + fieldName
		}

		// Apply validation rules
		for _, rule := range fv.rules {
			validator, ok := v.validators[rule.name]
			if !ok {
				errors = append(errors, ValidationError{
					Field:   fieldName,
					Message: fmt.Sprintf("unknown validator: %s", rule.name),
				})
				continue
			}

			// For eqfield validator, we need to pass the parent struct
			if rule.name == "eqfield" {
				if err := validateEqualFieldWithParent(field, rule.param, val); err != nil {
					errors = append(errors, ValidationError{
						Field:   fieldName,
						Message: err.Error(),
					})
				}
				continue
			}

			if err := validator(field, rule.param); err != nil {
				errors = append(errors, ValidationError{
					Field:   fieldName,
					Message: err.Error(),
				})
			}
		}

		// Recursively validate nested structs
		if field.Kind() == reflect.Struct || (field.Kind() == reflect.Ptr && field.Type().Elem().Kind() == reflect.Struct) {
			if nestedErrors := v.validate(field, fieldName); len(nestedErrors) > 0 {
				errors = append(errors, nestedErrors...)
			}
		}

		// Validate slices of structs
		if field.Kind() == reflect.Slice {
			for i := 0; i < field.Len(); i++ {
				item := field.Index(i)
				itemName := fmt.Sprintf("%s[%d]", fieldName, i)
				if itemErrors := v.validate(item, itemName); len(itemErrors) > 0 {
					errors = append(errors, itemErrors...)
				}
			}
		}
	}

	return errors
}

// getFieldValidations retrieves or creates cached field validation info
func (v *Validator) getFieldValidations(typ reflect.Type) []fieldValidation {
	// Check cache
	if cached, ok := v.tagCache[typ]; ok {
		return cached
	}

	// Parse and cache
	var validations []fieldValidation

	for i := 0; i < typ.NumField(); i++ {
		field := typ.Field(i)

		// Skip unexported fields
		if !field.IsExported() {
			continue
		}

		// Get validation tag
		tag := field.Tag.Get("validate")
		if tag == "" || tag == "-" {
			continue
		}

		// Parse rules
		rules := parseValidationRules(tag)
		if len(rules) == 0 {
			continue
		}

		validations = append(validations, fieldValidation{
			index: i,
			name:  field.Name,
			rules: rules,
		})
	}

	v.tagCache[typ] = validations
	return validations
}

// parseValidationRules parses a validation tag into individual rules
func parseValidationRules(tag string) []validationRule {
	var rules []validationRule

	// Split by comma
	parts := strings.Split(tag, ",")
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part == "" {
			continue
		}

		// Split by equals sign for parameterized rules
		if idx := strings.Index(part, "="); idx != -1 {
			rules = append(rules, validationRule{
				name:  part[:idx],
				param: part[idx+1:],
			})
		} else {
			rules = append(rules, validationRule{
				name: part,
			})
		}
	}

	return rules
}

// Built-in validator functions

func validateRequired(field reflect.Value, param string) error {
	if isZeroValue(field) {
		return fmt.Errorf("field is required")
	}
	return nil
}

func validateMin(field reflect.Value, param string) error {
	min, err := strconv.ParseFloat(param, 64)
	if err != nil {
		return fmt.Errorf("invalid min parameter: %s", param)
	}

	switch field.Kind() {
	case reflect.String:
		if float64(len(field.String())) < min {
			return fmt.Errorf("length must be at least %.0f", min)
		}
	case reflect.Slice, reflect.Array:
		if float64(field.Len()) < min {
			return fmt.Errorf("length must be at least %.0f", min)
		}
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		if float64(field.Int()) < min {
			return fmt.Errorf("value must be at least %.0f", min)
		}
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		if float64(field.Uint()) < min {
			return fmt.Errorf("value must be at least %.0f", min)
		}
	case reflect.Float32, reflect.Float64:
		if field.Float() < min {
			return fmt.Errorf("value must be at least %.2f", min)
		}
	}
	return nil
}

func validateMax(field reflect.Value, param string) error {
	max, err := strconv.ParseFloat(param, 64)
	if err != nil {
		return fmt.Errorf("invalid max parameter: %s", param)
	}

	switch field.Kind() {
	case reflect.String:
		if float64(len(field.String())) > max {
			return fmt.Errorf("length must be at most %.0f", max)
		}
	case reflect.Slice, reflect.Array:
		if float64(field.Len()) > max {
			return fmt.Errorf("length must be at most %.0f", max)
		}
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		if float64(field.Int()) > max {
			return fmt.Errorf("value must be at most %.0f", max)
		}
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		if float64(field.Uint()) > max {
			return fmt.Errorf("value must be at most %.0f", max)
		}
	case reflect.Float32, reflect.Float64:
		if field.Float() > max {
			return fmt.Errorf("value must be at most %.2f", max)
		}
	}
	return nil
}

func validateLen(field reflect.Value, param string) error {
	length, err := strconv.Atoi(param)
	if err != nil {
		return fmt.Errorf("invalid len parameter: %s", param)
	}

	switch field.Kind() {
	case reflect.String:
		if len(field.String()) != length {
			return fmt.Errorf("length must be exactly %d", length)
		}
	case reflect.Slice, reflect.Array:
		if field.Len() != length {
			return fmt.Errorf("length must be exactly %d", length)
		}
	default:
		return fmt.Errorf("len validator not supported for type %s", field.Kind())
	}
	return nil
}

var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$`)

func validateEmail(field reflect.Value, param string) error {
	if field.Kind() != reflect.String {
		return fmt.Errorf("email validator only works with strings")
	}

	email := field.String()
	if email == "" {
		return nil // Empty is valid unless required is also specified
	}

	if !emailRegex.MatchString(email) {
		return fmt.Errorf("invalid email format")
	}
	return nil
}

var urlRegex = regexp.MustCompile(`^https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=]+$`)

func validateURL(field reflect.Value, param string) error {
	if field.Kind() != reflect.String {
		return fmt.Errorf("url validator only works with strings")
	}

	url := field.String()
	if url == "" {
		return nil
	}

	if !urlRegex.MatchString(url) {
		return fmt.Errorf("invalid URL format")
	}
	return nil
}

func validateOneOf(field reflect.Value, param string) error {
	options := strings.Split(param, " ")
	value := fmt.Sprintf("%v", field.Interface())

	for _, opt := range options {
		if value == opt {
			return nil
		}
	}

	return fmt.Errorf("value must be one of: %s", strings.Join(options, ", "))
}

func validateGreaterThan(field reflect.Value, param string) error {
	threshold, err := strconv.ParseFloat(param, 64)
	if err != nil {
		return fmt.Errorf("invalid gt parameter: %s", param)
	}

	switch field.Kind() {
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		if float64(field.Int()) <= threshold {
			return fmt.Errorf("value must be greater than %.2f", threshold)
		}
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		if float64(field.Uint()) <= threshold {
			return fmt.Errorf("value must be greater than %.2f", threshold)
		}
	case reflect.Float32, reflect.Float64:
		if field.Float() <= threshold {
			return fmt.Errorf("value must be greater than %.2f", threshold)
		}
	default:
		return fmt.Errorf("gt validator not supported for type %s", field.Kind())
	}
	return nil
}

func validateGreaterThanEqual(field reflect.Value, param string) error {
	threshold, err := strconv.ParseFloat(param, 64)
	if err != nil {
		return fmt.Errorf("invalid gte parameter: %s", param)
	}

	switch field.Kind() {
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		if float64(field.Int()) < threshold {
			return fmt.Errorf("value must be at least %.2f", threshold)
		}
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		if float64(field.Uint()) < threshold {
			return fmt.Errorf("value must be at least %.2f", threshold)
		}
	case reflect.Float32, reflect.Float64:
		if field.Float() < threshold {
			return fmt.Errorf("value must be at least %.2f", threshold)
		}
	default:
		return fmt.Errorf("gte validator not supported for type %s", field.Kind())
	}
	return nil
}

func validateLessThan(field reflect.Value, param string) error {
	threshold, err := strconv.ParseFloat(param, 64)
	if err != nil {
		return fmt.Errorf("invalid lt parameter: %s", param)
	}

	switch field.Kind() {
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		if float64(field.Int()) >= threshold {
			return fmt.Errorf("value must be less than %.2f", threshold)
		}
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		if float64(field.Uint()) >= threshold {
			return fmt.Errorf("value must be less than %.2f", threshold)
		}
	case reflect.Float32, reflect.Float64:
		if field.Float() >= threshold {
			return fmt.Errorf("value must be less than %.2f", threshold)
		}
	default:
		return fmt.Errorf("lt validator not supported for type %s", field.Kind())
	}
	return nil
}

func validateLessThanEqual(field reflect.Value, param string) error {
	threshold, err := strconv.ParseFloat(param, 64)
	if err != nil {
		return fmt.Errorf("invalid lte parameter: %s", param)
	}

	switch field.Kind() {
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		if float64(field.Int()) > threshold {
			return fmt.Errorf("value must be at most %.2f", threshold)
		}
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		if float64(field.Uint()) > threshold {
			return fmt.Errorf("value must be at most %.2f", threshold)
		}
	case reflect.Float32, reflect.Float64:
		if field.Float() > threshold {
			return fmt.Errorf("value must be at most %.2f", threshold)
		}
	default:
		return fmt.Errorf("lte validator not supported for type %s", field.Kind())
	}
	return nil
}

func validateEqualField(field reflect.Value, param string) error {
	// This is handled specially in validate() to access parent struct
	return fmt.Errorf("eqfield validator requires parent struct context")
}

func validateEqualFieldWithParent(field reflect.Value, fieldName string, parent reflect.Value) error {
	otherField := parent.FieldByName(fieldName)
	if !otherField.IsValid() {
		return fmt.Errorf("field %s not found for comparison", fieldName)
	}

	if !reflect.DeepEqual(field.Interface(), otherField.Interface()) {
		return fmt.Errorf("must equal field %s", fieldName)
	}

	return nil
}

// isZeroValue checks if a reflect.Value is the zero value for its type
func isZeroValue(v reflect.Value) bool {
	switch v.Kind() {
	case reflect.Array, reflect.Map, reflect.Slice, reflect.String:
		return v.Len() == 0
	case reflect.Bool:
		return !v.Bool()
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return v.Int() == 0
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64, reflect.Uintptr:
		return v.Uint() == 0
	case reflect.Float32, reflect.Float64:
		return v.Float() == 0
	case reflect.Interface, reflect.Ptr:
		return v.IsNil()
	case reflect.Struct:
		// For structs, check if all fields are zero
		for i := 0; i < v.NumField(); i++ {
			if !isZeroValue(v.Field(i)) {
				return false
			}
		}
		return true
	}
	return false
}
