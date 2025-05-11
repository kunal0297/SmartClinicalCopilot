import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import threading
import queue
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from .metrics import PerformanceMetrics

logger = logging.getLogger(__name__)

@dataclass
class ConnectionInfo:
    """Connection information"""
    connection: Any
    created: datetime
    last_used: datetime
    in_use: bool
    error_count: int
    transaction_count: int

class ConnectionPool:
    """Advanced database connection pool"""
    
    def __init__(
        self,
        min_connections: int = 1,
        max_connections: int = 10,
        connection_timeout: int = 30,
        idle_timeout: int = 300,
        max_retries: int = 3,
        retry_delay: int = 1,
        **connection_params
    ):
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection_params = connection_params
        
        # Connection pool
        self.pool = pool.ThreadedConnectionPool(
            min_connections,
            max_connections,
            **connection_params
        )
        
        # Connection tracking
        self.connections: Dict[int, ConnectionInfo] = {}
        
        # Connection queue
        self.available_connections = queue.Queue()
        
        # Locks
        self.pool_lock = threading.Lock()
        self.connection_lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'waiting_connections': 0,
            'failed_connections': 0,
            'connection_errors': 0
        }
        
        # Initialize pool
        self._initialize_pool()
        
        # Start maintenance thread
        self.maintenance_thread = threading.Thread(
            target=self._maintenance_loop,
            daemon=True
        )
        self.maintenance_thread.start()
    
    def get_connection(self) -> Any:
        """Get a connection from the pool"""
        try:
            # Try to get connection from queue
            try:
                conn_id = self.available_connections.get(
                    timeout=self.connection_timeout
                )
            except queue.Empty:
                # Create new connection if possible
                with self.pool_lock:
                    if len(self.connections) < self.max_connections:
                        conn_id = self._create_connection()
                    else:
                        self.stats['waiting_connections'] += 1
                        raise Exception("No connections available")
            
            # Get connection from pool
            conn = self.pool.getconn(key=conn_id)
            
            # Update connection info
            with self.connection_lock:
                if conn_id in self.connections:
                    info = self.connections[conn_id]
                    info.in_use = True
                    info.last_used = datetime.utcnow()
                    info.transaction_count += 1
            
            # Update stats
            self.stats['active_connections'] += 1
            
            # Update metrics
            PerformanceMetrics.update_resource_utilization(
                len(self.connections) / self.max_connections,
                'database_connections'
            )
            
            return conn
            
        except Exception as e:
            logger.error("Error getting connection", exc_info=True)
            self.stats['connection_errors'] += 1
            raise
    
    def release_connection(self, connection: Any):
        """Release a connection back to the pool"""
        try:
            # Get connection ID
            conn_id = id(connection)
            
            # Update connection info
            with self.connection_lock:
                if conn_id in self.connections:
                    info = self.connections[conn_id]
                    info.in_use = False
                    info.last_used = datetime.utcnow()
            
            # Return connection to pool
            self.pool.putconn(connection, key=conn_id)
            
            # Add to available queue
            self.available_connections.put(conn_id)
            
            # Update stats
            self.stats['active_connections'] -= 1
            
        except Exception as e:
            logger.error("Error releasing connection", exc_info=True)
            self.stats['connection_errors'] += 1
    
    def close_connection(self, connection: Any):
        """Close a connection"""
        try:
            # Get connection ID
            conn_id = id(connection)
            
            # Remove from tracking
            with self.connection_lock:
                if conn_id in self.connections:
                    del self.connections[conn_id]
            
            # Close connection
            connection.close()
            
            # Update stats
            self.stats['total_connections'] -= 1
            self.stats['active_connections'] -= 1
            
        except Exception as e:
            logger.error("Error closing connection", exc_info=True)
            self.stats['connection_errors'] += 1
    
    def close_all(self):
        """Close all connections"""
        try:
            # Close all connections
            with self.connection_lock:
                for conn_id, info in list(self.connections.items()):
                    try:
                        info.connection.close()
                    except Exception:
                        pass
                
                self.connections.clear()
            
            # Close pool
            self.pool.closeall()
            
            # Reset stats
            self.stats = {
                'total_connections': 0,
                'active_connections': 0,
                'waiting_connections': 0,
                'failed_connections': 0,
                'connection_errors': 0
            }
            
        except Exception as e:
            logger.error("Error closing all connections", exc_info=True)
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            # Create minimum connections
            for _ in range(self.min_connections):
                self._create_connection()
                
        except Exception as e:
            logger.error("Error initializing pool", exc_info=True)
            self.stats['failed_connections'] += 1
    
    def _create_connection(self) -> int:
        """Create a new connection"""
        try:
            # Create connection
            conn = self.pool.getconn()
            
            # Get connection ID
            conn_id = id(conn)
            
            # Track connection
            with self.connection_lock:
                self.connections[conn_id] = ConnectionInfo(
                    connection=conn,
                    created=datetime.utcnow(),
                    last_used=datetime.utcnow(),
                    in_use=False,
                    error_count=0,
                    transaction_count=0
                )
            
            # Add to available queue
            self.available_connections.put(conn_id)
            
            # Update stats
            self.stats['total_connections'] += 1
            
            return conn_id
            
        except Exception as e:
            logger.error("Error creating connection", exc_info=True)
            self.stats['failed_connections'] += 1
            raise
    
    def _maintenance_loop(self):
        """Background maintenance loop"""
        while True:
            try:
                time.sleep(60)  # Check every minute
                self._maintain_pool()
            except Exception as e:
                logger.error("Error in maintenance loop", exc_info=True)
    
    def _maintain_pool(self):
        """Maintain connection pool"""
        try:
            current_time = datetime.utcnow()
            
            # Check connections
            with self.connection_lock:
                for conn_id, info in list(self.connections.items()):
                    # Check for idle connections
                    if not info.in_use and (
                        current_time - info.last_used
                    ).total_seconds() > self.idle_timeout:
                        # Close if above minimum
                        if len(self.connections) > self.min_connections:
                            self.close_connection(info.connection)
                    
                    # Check for error-prone connections
                    elif info.error_count >= self.max_retries:
                        self.close_connection(info.connection)
                    
                    # Check connection health
                    elif not info.in_use:
                        try:
                            with info.connection.cursor() as cur:
                                cur.execute('SELECT 1')
                        except Exception:
                            info.error_count += 1
                            if info.error_count >= self.max_retries:
                                self.close_connection(info.connection)
            
            # Ensure minimum connections
            while len(self.connections) < self.min_connections:
                self._create_connection()
                
        except Exception as e:
            logger.error("Error maintaining pool", exc_info=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        try:
            return {
                'total_connections': self.stats['total_connections'],
                'active_connections': self.stats['active_connections'],
                'waiting_connections': self.stats['waiting_connections'],
                'failed_connections': self.stats['failed_connections'],
                'connection_errors': self.stats['connection_errors'],
                'connection_details': {
                    conn_id: {
                        'created': info.created.isoformat(),
                        'last_used': info.last_used.isoformat(),
                        'in_use': info.in_use,
                        'error_count': info.error_count,
                        'transaction_count': info.transaction_count
                    }
                    for conn_id, info in self.connections.items()
                }
            }
        except Exception as e:
            logger.error("Error getting pool stats", exc_info=True)
            return {}
    
    def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        fetch: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
        """Execute a query with connection management"""
        conn = None
        try:
            # Get connection
            conn = self.get_connection()
            
            # Execute query
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                
                if fetch:
                    return cur.fetchall()
                else:
                    conn.commit()
                    return None
                    
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error("Error executing query", exc_info=True)
            raise
        finally:
            if conn:
                self.release_connection(conn)
    
    def execute_transaction(
        self,
        queries: List[Tuple[str, Optional[Tuple]]]
    ) -> List[Optional[List[Dict[str, Any]]]]:
        """Execute multiple queries in a transaction"""
        conn = None
        try:
            # Get connection
            conn = self.get_connection()
            
            # Start transaction
            conn.autocommit = False
            
            results = []
            
            # Execute queries
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                for query, params in queries:
                    cur.execute(query, params)
                    results.append(cur.fetchall())
            
            # Commit transaction
            conn.commit()
            
            return results
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error("Error executing transaction", exc_info=True)
            raise
        finally:
            if conn:
                conn.autocommit = True
                self.release_connection(conn)
    
    def execute_batch(
        self,
        query: str,
        params_list: List[Tuple]
    ) -> None:
        """Execute batch of queries"""
        conn = None
        try:
            # Get connection
            conn = self.get_connection()
            
            # Execute batch
            with conn.cursor() as cur:
                cur.executemany(query, params_list)
            
            # Commit
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error("Error executing batch", exc_info=True)
            raise
        finally:
            if conn:
                self.release_connection(conn)
    
    def execute_copy(
        self,
        query: str,
        data: List[Tuple]
    ) -> None:
        """Execute COPY command"""
        conn = None
        try:
            # Get connection
            conn = self.get_connection()
            
            # Execute COPY
            with conn.cursor() as cur:
                cur.copy_from(
                    query,
                    data,
                    sep='\t',
                    null='\\N'
                )
            
            # Commit
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error("Error executing COPY", exc_info=True)
            raise
        finally:
            if conn:
                self.release_connection(conn) 