import os
import asyncpg
import logging
import json
from typing import Optional, Dict, Any
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL")

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Create connection pool and ensure table exists"""
        if not DATABASE_URL:
            logging.error("DATABASE_URL environment variable is required but not set")
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Parse DATABASE_URL to extract connection details for logging
        parsed_url = urlparse(DATABASE_URL)
        db_name = parsed_url.path[1:] if parsed_url.path else 'N/A'  # Remove leading slash
        host = parsed_url.hostname or 'N/A'
        user = parsed_url.username or 'N/A'
        
        logging.info(f"Connecting to PostgreSQL database: {db_name}, Host: {host}, User: {user}")
        
        self.pool = await asyncpg.create_pool(DATABASE_URL)
        logging.info("Database connection pool created successfully")
        
        # Create table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS utm_clicks (
            id BIGSERIAL PRIMARY KEY,
            utm_params JSONB NOT NULL,
            ip_address INET,
            user_agent TEXT,
            referrer TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
        
        async with self.pool.acquire() as connection:
            await connection.execute(create_table_query)
            logging.info("utm_clicks table creation check completed successfully")
        
        # Verify table exists with a simple SELECT
        try:
            async with self.pool.acquire() as connection:
                await connection.execute("SELECT 1 FROM utm_clicks LIMIT 1")
                logging.info("utm_clicks table exists and is accessible")
        except Exception as e:
            logging.error(f"utm_clicks table verification failed: {type(e).__name__}: {e}")
            raise
        
        return self.pool

    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def insert_click(self, utm_params: Dict[str, Any], ip: str, user_agent: str, referrer: str):
        """Insert UTM click data into database using raw SQL"""
        if not self.pool:
            await self.connect()
        
        query = """
        INSERT INTO utm_clicks (utm_params, ip_address, user_agent, referrer, created_at)
        VALUES ($1, $2, $3, $4, NOW())
        """
        
        try:
            async with self.pool.acquire() as connection:
                # asyncpg expects JSONB values as JSON strings, not Python dicts
                await connection.execute(
                    query,
                    json.dumps(utm_params),
                    ip,
                    user_agent,
                    referrer
                )
                logging.info("Successfully inserted UTM click data into utm_clicks table")
        except Exception as e:
            logging.error(f"Database insert failed: {type(e).__name__}: {e}")
            raise

# Global database instance
db = Database()
