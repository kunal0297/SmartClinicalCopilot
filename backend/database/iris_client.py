import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import iris
from ..metrics.metrics_manager import MetricsManager
from ..cache_manager import CacheManager

logger = logging.getLogger(__name__)

class IRISClient:
    def __init__(self, connection_config: Dict[str, str]):
        self.config = connection_config
        self.connection = None
        self.metrics_manager = MetricsManager()
        self.cache_manager = CacheManager()
        self._validate_config()
        
    def _validate_config(self):
        required_fields = ["hostname", "port", "namespace", "username", "password"]
        missing_fields = [field for field in required_fields if field not in self.config]
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {missing_fields}")

    async def connect(self, max_retries: int = 3, retry_delay: int = 2):
        for attempt in range(max_retries):
            try:
                self.connection = iris.connect(
                    hostname=self.config["hostname"],
                    port=int(self.config["port"]),
                    namespace=self.config["namespace"],
                    username=self.config["username"],
                    password=self.config["password"],
                    timeout=self.config.get("timeout", 30)
                )
                await self.metrics_manager.record_connection_success()
                logger.info("Successfully connected to IRIS database")
                return
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                await self.metrics_manager.record_connection_failure()
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    raise

    async def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        cache_ttl: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        cache_key = f"query_{hash(query)}_{hash(str(params))}"
        
        if cache_ttl:
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result

        try:
            start_time = datetime.now()
            cursor = self.connection.cursor()
            cursor.execute(query, params or {})
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            query_time = (datetime.now() - start_time).total_seconds()
            await self.metrics_manager.record_query_metrics(query, query_time)
            
            if cache_ttl:
                await self.cache_manager.set(cache_key, results, ttl=cache_ttl)
            
            return results
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            await self.metrics_manager.record_query_error(query, str(e))
            raise
        finally:
            cursor.close()

    async def execute_batch(
        self,
        queries: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        results = []
        async with self.connection.transaction():
            for query_info in queries:
                try:
                    result = await self.execute_query(
                        query_info["query"],
                        query_info.get("params"),
                        query_info.get("cache_ttl")
                    )
                    results.append({
                        "success": True,
                        "data": result,
                        "query_id": query_info.get("id")
                    })
                except Exception as e:
                    results.append({
                        "success": False,
                        "error": str(e),
                        "query_id": query_info.get("id")
                    })
        return results

    async def close(self):
        if self.connection:
            self.connection.close()
            logger.info("IRIS database connection closed")