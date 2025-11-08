# Agent 11: API Schema Generator ⭐

**Complexity:** Beginner-Intermediate | **Framework:** `pydantic` + `ollama` | **Estimated Time:** 2-3 hours

---

## 🎯 Learning Objectives

- ✅ Generate OpenAPI/Swagger specifications
- ✅ Infer schemas from Python code
- ✅ Understand API documentation standards
- ✅ Use Pydantic for data validation
- ✅ Create API documentation automatically

## 🧠 Key Concepts

### OpenAPI Specification

OpenAPI (formerly Swagger) is the industry standard for describing REST APIs:

```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
```

### Schema Inference

The agent analyzes your code to automatically generate schemas:
- Function signatures → Path operations
- Type hints → Request/response schemas
- Docstrings → Descriptions
- Decorators → HTTP methods

## 🚀 Usage

```bash
# Generate OpenAPI spec from Flask/FastAPI app
python agent.py --app app.py --output openapi.yaml

# Generate from function signatures
python agent.py --file api_handlers.py

# Interactive mode
python agent.py --interactive
```

**Next:** [Agent 12: SQL Query Optimizer](../12_sql_optimizer/README.md) →
