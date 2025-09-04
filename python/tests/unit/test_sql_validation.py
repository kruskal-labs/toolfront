"""Unit tests for SQL validation in toolfront.models.database."""

from toolfront.models.database import Query


class TestQueryValidation:
    """Test cases for SQL query validation."""

    def test_read_only_select_queries(self):
        """Test that SELECT queries are allowed."""
        queries = [
            "SELECT * FROM users",
            "SELECT id, name FROM products WHERE price > 100",
            "SELECT COUNT(*) FROM orders",
            "select * from users",  # lowercase
            "  SELECT * FROM users  ",  # whitespace
        ]
        for sql in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is True

    def test_read_only_with_queries(self):
        """Test that WITH (CTE) queries are allowed."""
        queries = [
            "WITH cte AS (SELECT * FROM users) SELECT * FROM cte",
            """WITH RECURSIVE cte AS (
                SELECT 1 as n
                UNION ALL
                SELECT n + 1 FROM cte WHERE n < 10
            ) SELECT * FROM cte""",
        ]
        for sql in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is True

    def test_read_only_show_queries(self):
        """Test that SHOW queries are allowed."""
        queries = [
            "SHOW TABLES",
            "SHOW DATABASES",
            "SHOW COLUMNS FROM users",
            "show tables",  # lowercase
        ]
        for sql in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is True

    def test_read_only_describe_queries(self):
        """Test that DESCRIBE queries are allowed."""
        queries = [
            "DESCRIBE users",
            "DESCRIBE TABLE products",
            "describe users",  # lowercase
        ]
        for sql in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is True

    def test_read_only_explain_queries(self):
        """Test that EXPLAIN queries are allowed."""
        queries = [
            "EXPLAIN SELECT * FROM users",
            "EXPLAIN ANALYZE SELECT * FROM products",
            "explain select * from users",  # lowercase
        ]
        for sql in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is True

    def test_write_insert_queries(self):
        """Test that INSERT queries are rejected."""
        queries = [
            "INSERT INTO users (name) VALUES ('John')",
            "INSERT INTO products SELECT * FROM temp_products",
            "insert into users values (1, 'test')",  # lowercase
        ]
        for sql in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is False

    def test_write_update_queries(self):
        """Test that UPDATE queries are rejected."""
        queries = [
            "UPDATE users SET name = 'John' WHERE id = 1",
            "UPDATE products SET price = price * 1.1",
            "update users set active = false",  # lowercase
        ]
        for sql in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is False

    def test_write_delete_queries(self):
        """Test that DELETE queries are rejected."""
        queries = [
            "DELETE FROM users WHERE id = 1",
            "DELETE FROM products",
            "delete from orders where status = 'cancelled'",  # lowercase
        ]
        for sql in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is False

    def test_ddl_create_queries(self):
        """Test that CREATE queries are rejected."""
        queries = [
            "CREATE TABLE users (id INT, name VARCHAR(100))",
            "CREATE DATABASE test_db",
            "CREATE INDEX idx_users_name ON users(name)",
            "create view user_view as select * from users",  # lowercase
        ]
        for sql in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is False

    def test_ddl_drop_queries(self):
        """Test that DROP queries are rejected."""
        queries = [
            "DROP TABLE users",
            "DROP DATABASE test_db",
            "DROP INDEX idx_users_name",
            "drop view user_view",  # lowercase
        ]
        for sql in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is False

    def test_ddl_alter_queries(self):
        """Test that ALTER queries are rejected."""
        queries = [
            "ALTER TABLE users ADD COLUMN email VARCHAR(255)",
            "ALTER TABLE products DROP COLUMN description",
            "alter database test_db set timezone = 'UTC'",  # lowercase
        ]
        for sql in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is False

    def test_truncate_queries(self):
        """Test that TRUNCATE queries are rejected."""
        queries = [
            "TRUNCATE TABLE users",
            "TRUNCATE products",
            "truncate table orders",  # lowercase
        ]
        for sql in queries:
            query = Query(code=sql)
            assert query.is_read_only_query() is False

    def test_multiple_statements(self):
        """Test handling of multiple SQL statements."""
        # Multiple SELECT statements should be allowed
        query = Query(code="SELECT * FROM users; SELECT * FROM products")
        assert query.is_read_only_query() is True

        # Mix of read and write should be rejected
        query = Query(code="SELECT * FROM users; DELETE FROM products")
        assert query.is_read_only_query() is False

    def test_complex_queries(self):
        """Test complex SQL queries."""
        # Complex SELECT with joins
        query = Query(
            code="""
            SELECT u.name, COUNT(o.id) as order_count
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            WHERE u.created_at > '2023-01-01'
            GROUP BY u.id, u.name
            HAVING COUNT(o.id) > 5
            ORDER BY order_count DESC
            LIMIT 10
        """
        )
        assert query.is_read_only_query() is True

        # SELECT with subqueries
        query = Query(
            code="""
            SELECT * FROM users
            WHERE id IN (
                SELECT user_id FROM orders
                WHERE total > 1000
            )
        """
        )
        assert query.is_read_only_query() is True

    def test_sql_injection_attempts(self):
        """Test that potential SQL injection patterns are handled correctly."""
        # These should still be validated based on the main statement type
        queries = [
            "SELECT * FROM users WHERE name = 'test'; DROP TABLE users; --'",
            "SELECT * FROM users WHERE id = 1 OR 1=1",
        ]

        # First one has DROP, so should be rejected
        query = Query(code=queries[0])
        assert query.is_read_only_query() is False

        # Second one is still just a SELECT, so allowed
        query = Query(code=queries[1])
        assert query.is_read_only_query() is True

    def test_empty_and_whitespace_queries(self):
        """Test handling of empty or whitespace-only queries."""
        queries = [
            "",
            "   ",
            "\n\n",
            "\t",
        ]
        for sql in queries:
            query = Query(code=sql)
            # Empty queries should be considered read-only (no harm)
            assert query.is_read_only_query() is True
