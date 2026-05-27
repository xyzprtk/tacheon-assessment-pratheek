"""
Main orchestrator: Coordinates fetch, transform, and load steps.
"""
import logging
import sys
from datetime import date

from config import config
from fetch import fetch_all_pages, APIError
from transform import transform
from load import load_to_bigquery

logging.basicConfig(
    level=getattr(logging, config.log_level.upper()),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "event": "%(event)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    """
    Execute the full ETL pipeline: fetch, transform, load.
    """
    logger.info("Pipeline started", extra={"event": "pipeline_start"})
    
    try:
        logger.info("Step 1: Extracting data from CoinGecko API")
        raw_data = fetch_all_pages()
        
        if not raw_data:
            logger.warning(
                "No data fetched from API, exiting pipeline",
                extra={"event": "pipeline_no_data"}
            )
            sys.exit(0)
        
        logger.info("Step 2: Transforming data")
        df_transformed = transform(raw_data)
        
        if df_transformed.empty:
            logger.warning(
                "Transformed DataFrame is empty, exiting pipeline",
                extra={"event": "pipeline_empty_data"}
            )
            sys.exit(0)
        
        logger.info("Step 3: Loading data to BigQuery")
        target_date = date.today()
        load_to_bigquery(df_transformed, target_date)
        
        logger.info(
            "Pipeline completed successfully",
            extra={
                "event": "pipeline_complete",
                "rows_loaded": len(df_transformed),
                "target_date": str(target_date)
            }
        )
        
    except APIError as e:
        logger.error(
            f"Pipeline failed during extraction: {e}",
            extra={"event": "pipeline_error", "stage": "extract"}
        )
        sys.exit(1)
    
    except Exception as e:
        logger.error(
            f"Pipeline failed with unexpected error: {e}",
            extra={"event": "pipeline_error", "stage": "unknown"},
            exc_info=True
        )
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
