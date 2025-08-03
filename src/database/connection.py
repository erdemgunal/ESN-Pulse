"""
Database Connection Management

PostgreSQL veritabanı bağlantılarını yöneten modül.
Async context manager kullanarak connection pooling sağlar.
"""

import asyncio
import logging
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg
from asyncpg import Connection, Pool

from ..config import settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Asenkron PostgreSQL veritabanı bağlantı yöneticisi.
    
    Connection pooling ve transaction yönetimi sağlar.
    """
    
    def __init__(self):
        self.pool: Optional[Pool] = None
        self._connection_string = settings.DATABASE_URL
        
    async def initialize(self):
        """Initialize connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self._connection_string,
                min_size=1,
                max_size=settings.DATABASE_POOL_SIZE,
                max_queries=50000,
                max_inactive_connection_lifetime=300.0,
                command_timeout=60,
                server_settings={
                    'application_name': 'esn_pulse',
                    'search_path': 'public'
                }
            )
            
            logger.info(f"Database pool initialized with {settings.DATABASE_POOL_SIZE} connections")
            
            # Test connection
            async with self.pool.acquire() as conn:
                version = await conn.fetchval('SELECT version()')
                logger.info(f"Connected to: {version}")
                
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {str(e)}")
            raise
    
    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Connection, None]:
        """
        Get database connection from pool.
        
        Yields:
            asyncpg.Connection: Database connection
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"Database operation failed: {str(e)}")
                raise
    
    @asynccontextmanager
    async def get_transaction(self) -> AsyncGenerator[Connection, None]:
        """
        Get database connection with transaction.
        
        Yields:
            asyncpg.Connection: Database connection with active transaction
        """
        async with self.get_connection() as conn:
            async with conn.transaction():
                try:
                    yield conn
                except Exception as e:
                    logger.error(f"Transaction failed, rolling back: {str(e)}")
                    raise
    
    async def execute_query(
        self, 
        query: str, 
        *args, 
        fetch: str = "none"
    ):
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string
            *args: Query parameters
            fetch: Type of fetch ("none", "one", "many", "val")
            
        Returns:
            Query result based on fetch type
        """
        async with self.get_connection() as conn:
            if fetch == "none":
                return await conn.execute(query, *args)
            elif fetch == "one":
                return await conn.fetchrow(query, *args)
            elif fetch == "many":
                return await conn.fetch(query, *args)
            elif fetch == "val":
                return await conn.fetchval(query, *args)
            else:
                raise ValueError(f"Invalid fetch type: {fetch}")
    
    async def execute_transaction(self, queries_and_params):
        """
        Execute multiple queries in a transaction.
        
        Args:
            queries_and_params: List of (query, params) tuples
            
        Returns:
            List of query results
        """
        results = []
        
        async with self.get_transaction() as conn:
            for query, params in queries_and_params:
                result = await conn.execute(query, *params)
                results.append(result)
        
        return results
    
    async def bulk_insert(
        self, 
        table: str, 
        columns: list, 
        records: list
    ):
        """
        Bulk insert records using COPY.
        
        Args:
            table: Table name
            columns: List of column names
            records: List of tuples containing record data
        """
        async with self.get_connection() as conn:
            await conn.copy_records_to_table(
                table,
                records=records,
                columns=columns
            )
        
        logger.info(f"Bulk inserted {len(records)} records into {table}")
    
    async def health_check(self) -> bool:
        """
        Check database connectivity.
        
        Returns:
            True if database is accessible, False otherwise
        """
        try:
            async with self.get_connection() as conn:
                await conn.fetchval('SELECT 1')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None


async def get_db_connection() -> DatabaseConnection:
    """
    Get global database connection instance.
    
    Returns:
        DatabaseConnection: Initialized database connection
    """
    global _db_connection
    
    if _db_connection is None:
        _db_connection = DatabaseConnection()
        await _db_connection.initialize()
    
    return _db_connection


async def close_db_connection():
    """Close global database connection."""
    global _db_connection
    
    if _db_connection:
        await _db_connection.close()
        _db_connection = None


@asynccontextmanager
async def get_database_connection():
    """
    Async context manager for database connection.
    
    Usage:
        async with get_database_connection() as db:
            result = await db.execute_query("SELECT * FROM countries")
    """
    db = await get_db_connection()
    try:
        yield db
    finally:
        pass  # Connection is managed by the pool


@asynccontextmanager  
async def get_database_transaction():
    """
    Async context manager for database transaction.
    
    Usage:
        async with get_database_transaction() as conn:
            await conn.execute("INSERT INTO ...")
            await conn.execute("UPDATE ...")
    """
    db = await get_db_connection()
    async with db.get_transaction() as conn:
        yield conn 