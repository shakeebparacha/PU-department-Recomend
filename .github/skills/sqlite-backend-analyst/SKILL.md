---
name: sqlite-backend-analyst
description: 'Data Analyst and Backend Developer specialized in SQLite. Use when analyzing SQLite databases, writing queries, building backend API endpoints, or extracting data insights.'
---

# SQLite Backend Analyst

## When to Use
- You need to analyze the schema or data of an SQLite database.
- You are developing backend database operations, models, or APIs powered by SQLite.
- You need complex SQL queries, performance optimization, or data reporting from an `.sqlite` or `.db` file.

## Procedure

### 1. Database Discovery & Schema Analysis
- Locate the SQLite database files in the workspace (often `.db`, `.sqlite`, or `.sqlite3`).
- Analyze the tables, schemas, relationships, and indexes using SQLite specific commands (e.g., `PRAGMA table_info(table_name)`, `SELECT sqlite_schema`).
- Identify primary keys, foreign keys, and constraints.

### 2. Backend Implementation
- Structure the database connection safely using the environment's preferred language (e.g., Python `sqlite3`, SQLAlchemy, or Node.js `sqlite3`).
- Implement connection pooling and context managers if applicable.
- Write secure, parameterized queries to avoid SQL injection.

### 3. Data Analysis & Query Optimization
- Formulate aggregate queries (e.g., `GROUP BY`, `HAVING`) or window functions to extract necessary data insights.
- Check execution plans using `EXPLAIN QUERY PLAN` for complex queries.
- Optimize by proposing relevant indexes for frequently queried columns.

### 4. Code & Report Generation
- Combine the SQL logic with backend application code or analysis scripts.
- Present data insights cleanly or wrap the database operation in a robust backend function with error handling.

## Quality Criteria
- All queries must use parameterization.
- Database connections must be closed gracefully.
- Analytical queries should be optimized for performance.
