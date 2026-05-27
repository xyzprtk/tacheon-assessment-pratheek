# Production Thinking

This document covers production considerations for the CoinGecko data pipeline.

## Scheduling

### Cloud Scheduler + Cloud Run Jobs

For production deployment, the pipeline should run on a schedule using Cloud Scheduler to trigger Cloud Run Jobs.

**Why Cloud Run Jobs:**
- Serverless execution without VM maintenance
- Support for longer-running tasks (up to 60 minutes)
- Containerized deployment with Docker
- Built-in retry policies
- Native integration with Cloud Monitoring

**Deployment steps:**

1. Create a Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

2. Build and push to Container Registry:
```bash
gcloud builds submit --tag gcr.io/your-project/crypto-pipeline
```

3. Create a Cloud Run Job:
```bash
gcloud run jobs create crypto-pipeline-job \
  --image gcr.io/your-project/crypto-pipeline \
  --region us-central1 \
  --max-retries 3 \
  --task-timeout 10m \
  --set-env-vars="BQ_PROJECT_ID=your-project,BQ_DATASET_ID=crypto_market,BQ_TABLE_ID=coin_snapshots"
```

4. Schedule daily execution with Cloud Scheduler:
```bash
gcloud scheduler jobs create http crypto-pipeline-schedule \
  --schedule="0 9 * * *" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/your-project/jobs/crypto-pipeline-job:run" \
  --http-method=POST \
  --oauth-service-account-email=crypto-pipeline-sa@your-project.iam.gserviceaccount.com
```

## Observability

### Log-Based Alerting

Set up alerts in Cloud Monitoring:

1. Navigate to Cloud Monitoring > Alerting
2. Create a new alerting policy
3. Select log-based metric
4. Filter: `severity=ERROR AND resource.type="cloud_run_job"`
5. Set threshold: Alert if ERROR count > 0 in 5 minutes
6. Configure notification channel (email, Slack, or PagerDuty)

### Data Quality Checks

Run daily validation queries:

```sql
-- Check data freshness
SELECT
    COUNT(*) AS row_count,
    MAX(snapshot_timestamp) AS latest_snapshot
FROM `crypto_market.coin_snapshots`
WHERE snapshot_date = CURRENT_DATE();
```

Alert if:
- row_count is 0 (no data loaded)
- latest_snapshot is older than expected

### Monitoring Dashboard

Create a dashboard with:
- Pipeline execution duration
- Row counts per day
- Error rates
- API response times
- BigQuery load job status

## Scaling

### Current Limitations

The current implementation is designed for small to medium data volumes:
- Single-threaded API requests
- In-memory pandas processing
- Direct DataFrame loading to BigQuery

### Scaling to 10x Data Volume

| Component | Current Approach | Scaled Approach |
|-----------|-----------------|-----------------|
| **API Extraction** | Sequential requests loop | Parallel requests with asyncio/httpx, chunk by coin ID ranges, token bucket rate limiting |
| **Transformation** | pandas in-memory | polars (multi-core, lazy evaluation) or Apache Beam for distributed processing |
| **Storage Loading** | Direct DataFrame load | Stage as Parquet in Cloud Storage, then BigQuery Load Job from GCS |
| **BigQuery** | Partitioned by date | Add clustering, use Materialized Views for expensive aggregations |
| **Infrastructure** | Cloud Run Job (single container) | Dataflow (Apache Beam) for stream/batch hybrid, or Kubernetes CronJob with autoscaling |

### Horizontal Scaling

For very large datasets:
- Split coin list across multiple workers
- Each worker processes a subset of coins
- Aggregate results in a staging table
- Merge into final table

## Edge Cases and Resilience

### API Schema Drift

**Problem:** CoinGecko changes API response structure.

**Solution:**
- Validate response against expected schema using pydantic models
- Fail loudly if unknown fields appear
- Log schema validation errors with full response for debugging
- Set up alerts for schema validation failures

### Empty API Response

**Problem:** API returns empty array.

**Solution:**
- Check if response is empty before processing
- Log warning and exit gracefully
- Do not load empty DataFrame to BigQuery
- Alert if consecutive empty responses occur

### Partial Data (Null Fields)

**Problem:** Some fields are null in API response.

**Solution:**
- Enforce NULLABLE mode in BigQuery schema
- Keep as NaN/None in pandas
- Do not invent default values
- Document which fields can be null

### Duplicate Runs (Idempotency)

**Problem:** Pipeline runs multiple times for the same date.

**Solution:**
- Use WRITE_TRUNCATE on partition
- Re-running for the same date overwrites, not appends
- Ensures idempotent behavior

### BigQuery Quota Hit

**Problem:** BigQuery Sandbox has 1TB query limit per month.

**Solution:**
- Do heavy transforms in Python before loading
- Minimize BigQuery queries
- Use partition and clustering to reduce query costs
- Monitor quota usage

### Data Type Mismatch

**Problem:** API returns unexpected data types.

**Solution:**
- Use pd.to_numeric with errors='coerce' to convert invalid values to NaN
- NaN maps to NULL in BigQuery
- Log type conversion warnings

### Timezone Issues

**Problem:** Timestamps from different timezones.

**Solution:**
- Store everything as UTC in BigQuery
- Convert to UTC during transformation
- Handle display-time conversion in SQL queries or BI layer

### API Rate Limit (429)

**Problem:** CoinGecko rate limits requests.

**Solution:**
- Implement exponential backoff with tenacity
- Respect Retry-After header
- Space out requests between pages
- Add jitter to avoid thundering herd

### Network Timeout

**Problem:** Network issues cause timeouts.

**Solution:**
- Set explicit timeouts on requests: timeout=(connect=5, read=30)
- Retry like server errors
- Log timeout events for monitoring

## Cost Optimization

### BigQuery Costs

- Use partitioning to reduce query costs
- Cluster on frequently filtered columns
- Use SELECT specific columns instead of SELECT *
- Set up budget alerts in GCP

### Compute Costs

- Use Cloud Run Jobs (pay per execution)
- Set appropriate timeouts to avoid paying for hung jobs
- Use spot instances for non-critical workloads
- Right-size container memory and CPU

## Security

### Credentials Management

- Store service account keys outside project directory
- Use workload identity for Cloud Run Jobs
- Rotate credentials regularly
- Use Secret Manager for sensitive configuration

### Data Security

- BigQuery has encryption at rest by default
- Use VPC Service Controls to restrict data access
- Implement row-level security if needed
- Audit data access with Cloud Audit Logs

## Disaster Recovery

### Backup Strategy

- Export daily snapshots to Cloud Storage
- Use BigQuery table snapshots for point-in-time recovery
- Document recovery procedures
- Test recovery process regularly

### Failure Recovery

- Implement circuit breaker pattern for API calls
- Use dead letter queue for failed records
- Support manual retry through Cloud Console
- Document escalation procedures

## Future Enhancements

### Data Quality Framework

Integrate Great Expectations or Soda Core:
- Define expectations for data quality
- Run checks after transformation
- Fail pipeline if quality checks fail
- Generate data quality reports

### Incremental Loading

Instead of full refresh:
- Track last update timestamp for each coin
- Only fetch coins that changed since last run
- Reduce API calls and processing time

### Historical Backfill

- Support loading historical data for past dates
- Useful for initial data load or fixing past errors
- Implement date range parameter in main.py

### Real-time Updates

- Use CoinGecko WebSocket API for real-time updates
- Stream data to Pub/Sub
- Process with Dataflow
- Load into BigQuery streaming API

## Conclusion

This pipeline is designed for assessment purposes and works well for small to medium data volumes. For production use, implement the scaling, observability, and resilience patterns described above. The modular design makes it straightforward to enhance individual components without rewriting the entire system.
