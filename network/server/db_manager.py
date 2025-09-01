import os
import sqlite3
from typing import Dict

# DB 경로 및 연결 유틸
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "vending.db")


def _get_conn() -> sqlite3.Connection:
    """SQLite 연결 반환"""
    return sqlite3.connect(DB_PATH, isolation_level=None)  # auto-commit


def init_db() -> None:
    """테이블이 없으면 생성하고, 기존 데이터는 모두 삭제하여 초기화"""
    conn = _get_conn()
    cur = conn.cursor()

    # 판매 이력 테이블 생성
    cur.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                                                     id         INTEGER PRIMARY KEY AUTOINCREMENT,
                                                     machine_id TEXT,
                                                     date       TEXT,
                                                     beverage   TEXT,
                                                     count      INTEGER,
                                                     total      INTEGER
                );
                """)

    # 재고 현황 테이블 생성
    cur.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                                                         machine_id TEXT,
                                                         beverage   TEXT,
                                                         stock      INTEGER,
                                                         PRIMARY KEY (machine_id, beverage)
                    );
                """)

    # --- 데이터 초기화 로직 추가 ---
    print(f"[DB] '{os.path.basename(DB_PATH)}'의 기존 데이터를 삭제합니다.")
    cur.execute("DELETE FROM sales")
    cur.execute("DELETE FROM inventory")


    conn.close()
    print(f"[DB] '{os.path.basename(DB_PATH)}' 초기화 완료")


def save_sales_data(machine_id: str, sales: Dict[str, Dict[str, int]]) -> None:
    conn = _get_conn()
    cur = conn.cursor()
    rows = [
        (machine_id, info["date"], bev, info["count"], info["total"])
        for bev, info in sales.items()
    ]
    cur.executemany(
        "INSERT INTO sales(machine_id, date, beverage, count, total) VALUES(?,?,?,?,?)",
        rows
    )
    conn.close()
    print(f"[DB] 매출 {len(rows)}건 저장 ✅")


def save_inventory_data(machine_id: str, inv: Dict[str, int]) -> None:
    conn = _get_conn()
    cur = conn.cursor()
    rows = [(machine_id, bev, stock) for bev, stock in inv.items()]
    cur.executemany(
        """
        INSERT INTO inventory(machine_id, beverage, stock)
        VALUES(?,?,?)
            ON CONFLICT(machine_id, beverage)
        DO UPDATE SET stock = excluded.stock;
        """,
        rows
    )
    conn.close()
    print(f"[DB] 재고 {len(rows)}건 동기화 ✅")


# --- 웹 관리자용 데이터 조회 함수 ---
def fetch_total_sales() -> dict:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
                SELECT beverage, SUM(count) as total_count, SUM(total) as total_revenue
                FROM sales
                GROUP BY beverage
                ORDER BY total_revenue DESC
                """)
    rows = cur.fetchall()
    conn.close()
    sales_data = {row[0]: {"count": row[1], "total": row[2]} for row in rows}
    return sales_data


def fetch_all_inventory() -> dict:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT machine_id, beverage, stock FROM inventory ORDER BY machine_id, beverage")
    rows = cur.fetchall()
    conn.close()
    inventory_data = {}
    for machine_id, beverage, stock in rows:
        if machine_id not in inventory_data:
            inventory_data[machine_id] = {}
        inventory_data[machine_id][beverage] = stock
    return inventory_data


init_db()