"""MySQL Test Result Logger
===========================
Inserts overall test results into a MySQL database after each automation run.

The table schema expected::

    CREATE TABLE test_results (
        id          INT AUTO_INCREMENT PRIMARY KEY,
        Test_Date   DATE         NOT NULL,
        Test_Time   TIME         NOT NULL,
        Model       VARCHAR(50)  NOT NULL,
        `2D_Data`   VARCHAR(50)  NOT NULL,
        Test_Result VARCHAR(10)  NOT NULL
    );

Connection settings can be changed in the ``DB_CONFIG`` dict below.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

# ── Connection settings ── Change these to match your MySQL server ─────────────
DB_CONFIG = {
    "host":     "localhost",   # MySQL server hostname or IP
    "port":     3306,          # MySQL server port
    "database": "testbench",   # Database (schema) name
    "user":     "root",        # MySQL username
    "password": "password",    # MySQL password
}

# ── Table name ─────────────────────────────────────────────────────────────────
TABLE_NAME = "test_results"


def insert_test_result(
    model: str,
    scan_code: str,
    all_passed: bool,
    timestamp: Optional[datetime] = None,
) -> None:
    """Insert one row into the MySQL test_results table.

    :param model:      Model identifier — used as the *Model* column value.
                       Typically the same as the 2D scan code, but can be
                       customised if the model name differs from the scan code.
    :param scan_code:  The 2D barcode / scan value entered by the operator.
    :param all_passed: ``True`` → 'PASS', ``False`` → 'FAIL'.
    :param timestamp:  Datetime for the record; defaults to ``datetime.now()``.

    Raises ``ImportError`` when the ``mysql-connector-python`` package is not
    installed.  Any other exception (connection refused, auth failure, etc.) is
    re-raised to the caller so it can be logged without crashing the automation.
    """
    try:
        import mysql.connector  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "mysql-connector-python is not installed.\n"
            "Run:  pip install mysql-connector-python"
        ) from exc

    ts = timestamp or datetime.now()
    test_date = ts.strftime("%Y-%m-%d")
    test_time = ts.strftime("%H:%M:%S")
    test_result = "PASS" if all_passed else "FAIL"

    sql = (
        f"INSERT INTO `{TABLE_NAME}` "
        f"(Test_Date, Test_Time, Model, `2D_Data`, Test_Result) "
        f"VALUES (%s, %s, %s, %s, %s)"
    )
    values = (test_date, test_time, model, scan_code, test_result)

    conn = mysql.connector.connect(**DB_CONFIG)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()
