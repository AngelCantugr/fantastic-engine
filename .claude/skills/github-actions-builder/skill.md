# GitHub Actions Builder Skill

You are an expert at creating CI/CD workflows using GitHub Actions.

## When to Use

Activate when the user:
- Wants to set up CI/CD
- Mentions "GitHub Actions", "CI/CD", "automation", "workflows"
- Needs to automate testing, building, or deployment
- Wants to implement DevOps practices

## GitHub Actions Fundamentals

### Workflow
YAML file that defines automated process

### Job
Set of steps that execute on the same runner

### Step
Individual task (run command or action)

### Action
Reusable unit of code

### Trigger
Event that starts a workflow

## Output Format

```markdown
## 🚀 GitHub Actions Workflow: [Workflow Name]

### Purpose
[What this workflow does]

### Triggers
- [When it runs]
- [Branch conditions]

### Jobs
1. **[Job Name]**: [Description]
2. **[Job Name]**: [Description]

---

## Workflow File

**Path:** `.github/workflows/[name].yml`

```yaml
[Workflow YAML content]
```

---

## Setup Instructions

1. Create the workflow file:
   ```bash
   mkdir -p .github/workflows
   ```

2. Add the workflow file above

3. Push to GitHub:
   ```bash
   git add .github/workflows/
   git commit -m "Add GitHub Actions workflow"
   git push
   ```

4. View workflow runs:
   - Go to repository → Actions tab

---

## Customization

[Tips for adapting the workflow]

## Secrets Required

- `SECRET_NAME`: Description of what it's for
```

## Common Workflow Triggers

```yaml
# Push to specific branches
on:
  push:
    branches: [main, develop]

# Pull requests
on:
  pull_request:
    branches: [main]

# Multiple triggers
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Schedule (cron)
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

# Manual trigger
on:
  workflow_dispatch:

# Specific paths
on:
  push:
    paths:
      - 'src/**'
      - '**.js'

# Ignore paths
on:
  push:
    paths-ignore:
      - 'docs/**'
      - '**.md'

# Release events
on:
  release:
    types: [published]
```

## Workflow Examples

### Node.js CI/CD

```yaml
name: Node.js CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test

      - name: Run build
        run: npm run build

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20.x'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Deploy to production
        run: npm run deploy
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

### Python CI

```yaml
name: Python CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linter
        run: |
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127

      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Docker Build & Push

```yaml
name: Docker Build and Push

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Deploy to AWS

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: my-app
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster my-cluster \
            --service my-service \
            --force-new-deployment
```

### Automated Releases

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20.x'
          registry-url: 'https://registry.npmjs.org'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Publish to npm
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

      - name: Generate changelog
        id: changelog
        uses: metcalfc/changelog-generator@v4.1.0
        with:
          myToken: ${{ secrets.GITHUB_TOKEN }}

      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body: ${{ steps.changelog.outputs.changelog }}
          draft: false
          prerelease: false
```

### Monorepo with Matrix

```yaml
name: Monorepo CI

on: [push, pull_request]

jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      packages: ${{ steps.filter.outputs.changes }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: filter
        with:
          filters: |
            package-a:
              - 'packages/package-a/**'
            package-b:
              - 'packages/package-b/**'
            package-c:
              - 'packages/package-c/**'

  test:
    needs: changes
    if: ${{ needs.changes.outputs.packages != '[]' }}
    runs-on: ubuntu-latest

    strategy:
      matrix:
        package: ${{ fromJSON(needs.changes.outputs.packages) }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20.x'

      - name: Install dependencies
        run: npm ci

      - name: Test ${{ matrix.package }}
        working-directory: packages/${{ matrix.package }}
        run: |
          npm run lint
          npm test
```

## Reusable Workflows

### Called Workflow

**.github/workflows/reusable-test.yml**

```yaml
name: Reusable Test Workflow

on:
  workflow_call:
    inputs:
      node-version:
        required: true
        type: string
    secrets:
      token:
        required: true

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}

      - run: npm ci
      - run: npm test
```

### Calling Workflow

**.github/workflows/main.yml**

```yaml
name: Main Workflow

on: [push]

jobs:
  call-test:
    uses: ./.github/workflows/reusable-test.yml
    with:
      node-version: '20.x'
    secrets:
      token: ${{ secrets.MY_TOKEN }}
```

## Custom Actions

### JavaScript Action

```yaml
# action.yml
name: 'My Custom Action'
description: 'Does something custom'
inputs:
  input-param:
    description: 'Input parameter'
    required: true
outputs:
  output-param:
    description: 'Output parameter'
runs:
  using: 'node20'
  main: 'index.js'
```

### Docker Action

```yaml
# action.yml
name: 'Docker Action'
description: 'Runs in Docker'
inputs:
  param:
    description: 'Parameter'
    required: true
runs:
  using: 'docker'
  image: 'Dockerfile'
  args:
    - ${{ inputs.param }}
```

## Conditional Execution

```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy
        if: success() && !cancelled()
        run: npm run deploy

      - name: Notify on failure
        if: failure()
        run: echo "Deployment failed!"

      - name: Always run cleanup
        if: always()
        run: echo "Cleanup..."
```

## Secrets Management

```yaml
steps:
  - name: Use secret
    run: echo "Secret is ${{ secrets.MY_SECRET }}"
    env:
      API_KEY: ${{ secrets.API_KEY }}

  # Secrets are automatically masked in logs
```

**Setting secrets:**
1. Go to Repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add name and value

## Environment Variables

```yaml
env:
  # Workflow-level
  GLOBAL_VAR: 'global'

jobs:
  build:
    env:
      # Job-level
      JOB_VAR: 'job'

    steps:
      - name: Step with env
        env:
          # Step-level
          STEP_VAR: 'step'
        run: |
          echo "Global: $GLOBAL_VAR"
          echo "Job: $JOB_VAR"
          echo "Step: $STEP_VAR"
```

## Caching Dependencies

```yaml
steps:
  - uses: actions/checkout@v4

  # NPM cache
  - uses: actions/cache@v3
    with:
      path: ~/.npm
      key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
      restore-keys: |
        ${{ runner.os }}-node-

  # Pip cache
  - uses: actions/cache@v3
    with:
      path: ~/.cache/pip
      key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

  # Gradle cache
  - uses: actions/cache@v3
    with:
      path: |
        ~/.gradle/caches
        ~/.gradle/wrapper
      key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
```

## Artifacts

```yaml
jobs:
  build:
    steps:
      - run: npm run build

      # Upload artifact
      - uses: actions/upload-artifact@v3
        with:
          name: build-output
          path: dist/

  deploy:
    needs: build
    steps:
      # Download artifact
      - uses: actions/download-artifact@v3
        with:
          name: build-output
          path: dist/

      - run: npm run deploy
```

## Best Practices

### 1. Pin Action Versions

```yaml
# ✅ Good - Pin to specific SHA
- uses: actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab  # v4.1.1

# ✅ Good - Use version tag
- uses: actions/checkout@v4

# ❌ Bad - Using latest
- uses: actions/checkout@main
```

### 2. Fail Fast

```yaml
strategy:
  fail-fast: true  # Stop all jobs if one fails
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
```

### 3. Timeout Jobs

```yaml
jobs:
  build:
    timeout-minutes: 30  # Prevent hung jobs
    steps:
      - run: npm test
```

### 4. Use Concurrency

```yaml
# Cancel in-progress runs for the same PR
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Debugging Workflows

### Enable Debug Logging

Add repository secrets:
- `ACTIONS_RUNNER_DEBUG`: `true`
- `ACTIONS_STEP_DEBUG`: `true`

### Use tmate for SSH access

```yaml
- name: Setup tmate session
  if: failure()
  uses: mxschmitt/action-tmate@v3
```

## ADHD-Friendly GitHub Actions

### Start with a Template

GitHub provides starter workflows:
1. Go to Actions tab
2. Click "New workflow"
3. Choose a template

### Test Locally

Use `act` to run Actions locally:
```bash
npm install -g act
act
```

### One Job at a Time

Get one job working before adding more

### Use Workflow Visualizer

GitHub shows a visual graph of your workflow

### Copy Working Examples

Find similar projects and adapt their workflows
