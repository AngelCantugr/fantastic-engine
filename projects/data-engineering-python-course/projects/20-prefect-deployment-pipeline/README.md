# Project 20: Prefect Deployment Pipeline

**Complexity:** ⭐⭐⭐⭐☆ | **Time:** 8-10 hours | **Tier:** Advanced Intermediate

## Overview

Build a production-ready data pipeline using Prefect, a modern workflow orchestration platform. This project teaches event-driven workflows, dynamic task mapping, deployment strategies, and observability for data pipelines.

## Learning Objectives

After completing this project, you will understand:

- ✅ Modern workflow orchestration with Prefect
- ✅ Flows, tasks, and subflows architecture
- ✅ Dynamic task mapping and parallelism
- ✅ Deployment patterns (agents, work pools, workers)
- ✅ Event-driven workflow triggers
- ✅ State management and caching
- ✅ Observability and monitoring
- ✅ Multi-environment deployments

## Architecture

```mermaid
graph TD
    A[Prefect Cloud/Server] --> B[Work Pool]
    B --> C[Worker 1]
    B --> D[Worker 2]
    B --> E[Worker 3]

    F[Flow Deployment] --> A
    G[Schedule/Event Trigger] --> A

    C --> H[Flow Execution]
    D --> H
    E --> H

    H --> I[Task 1]
    H --> J[Task 2: Parallel]
    H --> K[Task 3]

    I --> J
    J --> K

    L[State Backend] --> H
    M[Results Storage: S3] --> H

    style A fill:#9370db,stroke:#00ffff
    style H fill:#00ff00,stroke:#00ffff
    style M fill:#ffff00,stroke:#00ffff
```

## Key Concepts

### Prefect Architecture

```mermaid
graph LR
    subgraph "Prefect Server/Cloud"
    A[API] --> B[Database]
    A --> C[Event System]
    end

    subgraph "Execution"
    D[Worker] --> E[Flow Run]
    E --> F[Task Runs]
    end

    D -->|Polls| A
    F -->|Reports State| A

    G[Deployment] -->|Creates| E

    style A fill:#9370db,stroke:#00ffff
    style E fill:#00ff00,stroke:#00ffff
```

**Key Components:**
- **Flow:** Container for workflow logic
- **Task:** Unit of work within a flow
- **Deployment:** Packaged flow with infrastructure config
- **Work Pool:** Queue for flow runs
- **Worker:** Executes flows from work pool

### Flow vs Task

```python
# Flow: Orchestration logic
@flow
def my_pipeline():
    result1 = extract_data()  # Task
    result2 = transform_data(result1)  # Task
    load_data(result2)  # Task

# Task: Actual work
@task
def extract_data():
    return data
```

### Dynamic Task Mapping

```mermaid
graph TD
    A[Flow Start] --> B[Generate Items]
    B --> C{Map Task}
    C -->|Item 1| D1[Process 1]
    C -->|Item 2| D2[Process 2]
    C -->|Item 3| D3[Process 3]
    D1 --> E[Collect Results]
    D2 --> E
    D3 --> E
    E --> F[Flow End]

    style C fill:#ffff00,stroke:#00ffff
    style E fill:#00ff00,stroke:#00ffff
```

## Implementation Guide

### Step 1: Basic Flow and Task Structure

```python
# pipeline.py
from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner, DaskTaskRunner
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

@task(name="extract_from_api", retries=3, retry_delay_seconds=60)
def extract_data_from_api(
    api_url: str,
    date: datetime
) -> pd.DataFrame:
    """
    Extract data from API.

    Features:
    - Automatic retries on failure
    - Retry delay
    - State tracking
    """
    logger.info(f"Extracting data for {date}")

    # Your extraction logic
    import requests
    response = requests.get(f"{api_url}/data?date={date.isoformat()}")
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data)

    logger.info(f"Extracted {len(df)} records")
    return df

@task(name="transform_data", cache_key_fn=lambda *args, **kwargs: "transform_cache")
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform data with caching.

    Cache results to avoid re-computation on retry.
    """
    logger.info("Transforming data")

    # Your transformation logic
    df_clean = df.dropna()
    df_clean['processed_at'] = datetime.now()

    logger.info(f"Transformed {len(df_clean)} records")
    return df_clean

@task(name="load_to_warehouse")
def load_data(df: pd.DataFrame, table_name: str):
    """Load data to data warehouse."""
    logger.info(f"Loading {len(df)} records to {table_name}")

    # Your loading logic
    from sqlalchemy import create_engine
    engine = create_engine("postgresql://user:pass@localhost/db")
    df.to_sql(table_name, engine, if_exists='append', index=False)

    logger.info("Load complete")

@flow(
    name="daily_etl_pipeline",
    description="Daily ETL pipeline with Prefect",
    retries=2,
    retry_delay_seconds=300
)
def daily_etl_pipeline(
    api_url: str,
    table_name: str,
    date: datetime = None
):
    """
    Main ETL pipeline flow.

    Args:
        api_url: API endpoint URL
        table_name: Target table name
        date: Date to process (defaults to yesterday)
    """
    if date is None:
        date = datetime.now() - timedelta(days=1)

    logger.info(f"Starting ETL pipeline for {date}")

    # Extract
    df = extract_data_from_api(api_url, date)

    # Transform
    df_transformed = transform_data(df)

    # Load
    load_data(df_transformed, table_name)

    logger.info("Pipeline complete!")

    return {
        'date': date.isoformat(),
        'records_processed': len(df_transformed)
    }
```

### Step 2: Dynamic Task Mapping and Parallelism

```python
# parallel_pipeline.py
from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner
from typing import List
import concurrent.futures

@task
def process_partition(partition_id: int, data: List[Dict]) -> Dict:
    """Process a single partition of data."""
    logger.info(f"Processing partition {partition_id}")

    # Your processing logic
    result = {
        'partition_id': partition_id,
        'records_processed': len(data),
        'status': 'success'
    }

    return result

@flow(
    task_runner=ConcurrentTaskRunner()  # Enable parallel execution
)
def parallel_processing_pipeline(data_partitions: List[List[Dict]]):
    """
    Process data partitions in parallel.

    Uses dynamic task mapping to spawn tasks for each partition.
    """
    logger.info(f"Processing {len(data_partitions)} partitions in parallel")

    # Map task across partitions (runs in parallel)
    results = process_partition.map(
        partition_id=range(len(data_partitions)),
        data=data_partitions
    )

    logger.info("All partitions processed")
    return results

# Example with Dask for distributed processing
@flow(
    task_runner=DaskTaskRunner(
        cluster_kwargs={
            "n_workers": 4,
            "threads_per_worker": 2
        }
    )
)
def distributed_pipeline(large_dataset: pd.DataFrame):
    """
    Process large dataset with Dask distributed executor.

    Automatically distributes tasks across Dask cluster.
    """
    # Split data into chunks
    chunks = [large_dataset[i:i+10000] for i in range(0, len(large_dataset), 10000)]

    # Process chunks in parallel on Dask cluster
    results = process_chunk.map(chunks)

    return results

@task
def process_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """Process a chunk of data."""
    # Your processing logic
    return chunk
```

### Step 3: Deployment Configuration

```python
# deployment.py
from prefect import flow
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule, IntervalSchedule
from prefect.filesystems import S3
from datetime import timedelta

# Define flow (same as above)
@flow
def my_etl_pipeline():
    # ... flow logic ...
    pass

# Create deployment
deployment = Deployment.build_from_flow(
    flow=my_etl_pipeline,
    name="production-etl",
    version="1.0.0",

    # Schedule: Run daily at 2 AM
    schedule=CronSchedule(cron="0 2 * * *", timezone="America/New_York"),

    # Or use interval schedule
    # schedule=IntervalSchedule(interval=timedelta(hours=6)),

    # Work pool and queue
    work_pool_name="production-pool",
    work_queue_name="default",

    # Parameters
    parameters={
        "api_url": "https://api.example.com",
        "table_name": "staging.daily_data"
    },

    # Infrastructure
    infra_overrides={
        "env": {
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO"
        }
    },

    # Storage for flow code (optional)
    # storage=S3(bucket_path="s3://my-bucket/flows/"),

    # Tags for organization
    tags=["production", "etl", "daily"]
)

if __name__ == "__main__":
    # Apply deployment
    deployment.apply()
```

### Step 4: Advanced Flow Patterns

```python
# advanced_flows.py
from prefect import flow, task
from prefect.futures import wait
from prefect.states import Completed, Failed
from typing import Optional
import asyncio

# Subflows for modularity
@flow(name="data_quality_checks")
def run_quality_checks(df: pd.DataFrame) -> bool:
    """
    Subflow for data quality validation.

    Can be reused across multiple parent flows.
    """
    logger.info("Running quality checks")

    # Check 1: No nulls in critical columns
    if df[['id', 'timestamp']].isnull().any().any():
        raise ValueError("Null values in critical columns")

    # Check 2: Data within expected range
    if len(df) < 100:
        logger.warning("Low record count")

    logger.info("Quality checks passed")
    return True

@flow(name="etl_with_validation")
def etl_with_validation_flow(api_url: str):
    """
    ETL flow with data quality validation subflow.
    """
    # Extract
    df = extract_data_from_api(api_url, datetime.now())

    # Validate
    is_valid = run_quality_checks(df)

    if is_valid:
        # Transform and load
        df_transformed = transform_data(df)
        load_data(df_transformed, "validated_data")
    else:
        logger.error("Quality checks failed, skipping load")

# Conditional branching
@task
def check_file_exists(file_path: str) -> bool:
    """Check if file exists."""
    from pathlib import Path
    return Path(file_path).exists()

@flow
def conditional_processing_flow(file_path: str):
    """
    Flow with conditional task execution.
    """
    exists = check_file_exists(file_path)

    if exists:
        logger.info("File exists, processing...")
        # Process file
    else:
        logger.info("File doesn't exist, skipping...")
        # Handle missing file

# Async flows for I/O-bound operations
@task
async def async_api_call(url: str) -> Dict:
    """Async API call."""
    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@flow
async def async_data_pipeline(urls: List[str]):
    """
    Async flow for concurrent I/O operations.

    Much faster than sequential for I/O-bound tasks.
    """
    # Call all APIs concurrently
    results = await asyncio.gather(*[
        async_api_call(url) for url in urls
    ])

    return results

# Error handling and notifications
@task
def send_failure_notification(error_message: str):
    """Send notification on pipeline failure."""
    # Send to Slack, email, PagerDuty, etc.
    logger.error(f"ALERT: Pipeline failed - {error_message}")

@flow(
    on_failure=[send_failure_notification],
    on_completion=[lambda flow, state: logger.info("Flow completed!")]
)
def pipeline_with_notifications():
    """
    Flow with automatic failure notifications.
    """
    try:
        # Pipeline logic
        result = extract_data_from_api("https://api.example.com", datetime.now())
    except Exception as e:
        send_failure_notification(str(e))
        raise
```

### Step 5: Observability and Monitoring

```python
# monitoring.py
from prefect import flow, task, get_run_logger
from prefect.blocks.notifications import SlackWebhook
from prefect.context import get_run_context
import time

@task
def monitored_task(data: pd.DataFrame) -> pd.DataFrame:
    """
    Task with detailed logging and metrics.
    """
    logger = get_run_logger()
    context = get_run_context()

    # Log task info
    logger.info(f"Task: {context.task.name}")
    logger.info(f"Input size: {len(data)} records")

    # Track timing
    start_time = time.time()

    # Process data
    result = data.copy()

    # Log metrics
    duration = time.time() - start_time
    logger.info(f"Processing took {duration:.2f} seconds")
    logger.info(f"Output size: {len(result)} records")

    return result

@flow
def monitored_pipeline():
    """
    Pipeline with comprehensive monitoring.
    """
    logger = get_run_logger()
    context = get_run_context()

    # Log flow run info
    logger.info(f"Flow run ID: {context.flow_run.id}")
    logger.info(f"Flow run name: {context.flow_run.name}")

    # Track overall pipeline metrics
    pipeline_start = time.time()

    # Run pipeline
    data = extract_data_from_api("https://api.example.com", datetime.now())
    result = monitored_task(data)

    # Log final metrics
    pipeline_duration = time.time() - pipeline_start
    logger.info(f"Total pipeline duration: {pipeline_duration:.2f} seconds")

    return {
        'duration': pipeline_duration,
        'records_processed': len(result),
        'status': 'success'
    }

# Slack notifications
def send_slack_notification(webhook_url: str, message: str):
    """Send Slack notification."""
    slack = SlackWebhook(url=webhook_url)
    slack.notify(message)

@flow(
    on_failure=[
        lambda: send_slack_notification(
            "https://hooks.slack.com/...",
            "Pipeline failed!"
        )
    ]
)
def pipeline_with_slack_alerts():
    """Pipeline with Slack notifications."""
    # Pipeline logic
    pass
```

## Nuanced Scenarios

### 1. Dynamic Task Mapping with Dependencies

**Challenge:** Map tasks dynamically while maintaining dependencies.

```python
@flow
def complex_mapping_flow(items: List[str]):
    """
    Complex dynamic mapping with dependencies.
    """
    # Stage 1: Process all items in parallel
    stage1_results = process_item.map(items)

    # Wait for all stage 1 tasks to complete
    wait(stage1_results)

    # Stage 2: Aggregate results (depends on all stage 1 tasks)
    aggregated = aggregate_results(stage1_results)

    # Stage 3: Map based on aggregated results
    final_results = finalize.map(aggregated)

    return final_results
```

### 2. Multi-Environment Deployments

**Challenge:** Deploy same flow to dev, staging, and production.

```python
# multi_env_deployment.py
from prefect.deployments import Deployment

environments = {
    'dev': {
        'work_pool': 'dev-pool',
        'schedule': None,  # Manual trigger only
        'parameters': {
            'api_url': 'https://dev-api.example.com',
            'table_name': 'dev.data'
        }
    },
    'staging': {
        'work_pool': 'staging-pool',
        'schedule': CronSchedule(cron="0 */6 * * *"),  # Every 6 hours
        'parameters': {
            'api_url': 'https://staging-api.example.com',
            'table_name': 'staging.data'
        }
    },
    'production': {
        'work_pool': 'production-pool',
        'schedule': CronSchedule(cron="0 2 * * *"),  # Daily at 2 AM
        'parameters': {
            'api_url': 'https://api.example.com',
            'table_name': 'prod.data'
        }
    }
}

# Create deployment for each environment
for env_name, config in environments.items():
    deployment = Deployment.build_from_flow(
        flow=my_etl_pipeline,
        name=f"{env_name}-deployment",
        work_pool_name=config['work_pool'],
        schedule=config['schedule'],
        parameters=config['parameters'],
        tags=[env_name]
    )
    deployment.apply()
```

### 3. Event-Driven Workflows

**Challenge:** Trigger flows based on external events (S3, webhooks, etc.).

```python
# event_driven.py
from prefect import flow
from prefect.events import Event, emit_event
from prefect.blocks.webhook import Webhook

@flow
def s3_triggered_pipeline(bucket: str, key: str):
    """
    Pipeline triggered by S3 event.

    Can be triggered by:
    - S3 Event Notifications to Lambda to Webhook
    - Direct integration with Prefect events
    """
    logger.info(f"Processing new file: s3://{bucket}/{key}")

    # Download and process file
    import boto3
    s3 = boto3.client('s3')
    s3.download_file(bucket, key, '/tmp/data.csv')

    # Process data
    df = pd.read_csv('/tmp/data.csv')
    result = transform_data(df)

    return result

# Emit custom events
@task
def process_with_events(data: pd.DataFrame):
    """
    Task that emits custom events.
    """
    # Emit start event
    emit_event(
        event="processing.started",
        resource={"prefect.resource.id": "data-pipeline"}
    )

    # Process data
    result = data.copy()

    # Emit completion event
    emit_event(
        event="processing.completed",
        resource={"prefect.resource.id": "data-pipeline"},
        payload={"records": len(result)}
    )

    return result
```

### 4. State Management and Caching

**Challenge:** Optimize performance with intelligent caching.

```python
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1)
)
def expensive_computation(input_data: str) -> pd.DataFrame:
    """
    Cache results for 1 hour.

    If called again with same input within 1 hour,
    returns cached result without re-execution.
    """
    logger.info("Computing (this is expensive)...")
    time.sleep(10)  # Simulate expensive operation

    # Your computation
    result = pd.DataFrame()

    return result

@task(persist_result=True)
def important_task(data: pd.DataFrame) -> pd.DataFrame:
    """
    Persist result to storage for recovery.

    If flow fails and restarts, this result can be reused.
    """
    # Your processing
    result = data.copy()

    return result
```

## Exercises

### Exercise 1: Basic Flow Creation
Create a simple ETL flow with Prefect:
- Extract from CSV
- Transform data
- Load to database
- Add retry logic

### Exercise 2: Parallel Processing
Build a flow with dynamic task mapping:
- Process multiple files in parallel
- Use ConcurrentTaskRunner
- Aggregate results
- Measure speedup

### Exercise 3: Deployment
Deploy flow to Prefect Cloud/Server:
- Configure work pool
- Set up schedule
- Add parameters
- Test deployment

### Exercise 4: Monitoring and Alerts
Add observability to pipeline:
- Custom logging
- Slack notifications
- Metrics tracking
- SLA monitoring

## Success Criteria

- [ ] Build parameterized data pipeline
- [ ] Deploy to Prefect Cloud/Server
- [ ] Implement monitoring and alerts
- [ ] Handle failures gracefully with retries
- [ ] Use dynamic task mapping for parallelism
- [ ] Configure multi-environment deployments
- [ ] Integrate with external triggers
- [ ] Achieve <1 minute deployment time

## Testing Checklist

```python
# tests/test_prefect_pipeline.py

def test_flow_execution():
    """Test flow executes successfully."""
    pass

def test_task_retry():
    """Test task retry on failure."""
    pass

def test_dynamic_mapping():
    """Test dynamic task mapping."""
    pass

def test_caching():
    """Test result caching."""
    pass

def test_deployment_creation():
    """Test deployment configuration."""
    pass

def test_parallel_execution():
    """Test concurrent task execution."""
    pass

def test_error_handling():
    """Test error handling and notifications."""
    pass

def test_subflows():
    """Test subflow execution."""
    pass
```

## Common Pitfalls

1. **Missing Retry Logic:** Tasks fail without retries in transient error cases
2. **No Caching:** Expensive computations re-run unnecessarily
3. **Poor Parallelism:** Not using task mapping for parallelizable work
4. **Hardcoded Parameters:** Deployments not parameterized properly
5. **No Monitoring:** Lack of observability into pipeline health
6. **Large Results:** Storing large results in memory instead of external storage
7. **No Testing:** Flows not tested before deployment

## Next Steps

After completing this project:
1. Move to **Tier 3 Projects** (Expert Level)
2. Combine Prefect with **Project 12: Apache Spark Pipeline**
3. Use with **Project 18: S3 Data Lake Organization**

## References

- [Prefect Documentation](https://docs.prefect.io/)
- [Prefect Cloud](https://www.prefect.io/cloud)
- [Flow and Task Patterns](https://docs.prefect.io/concepts/flows/)
- [Deployments Guide](https://docs.prefect.io/concepts/deployments/)
- [Task Runners](https://docs.prefect.io/concepts/task-runners/)

---

**Happy Learning! 🚀**
