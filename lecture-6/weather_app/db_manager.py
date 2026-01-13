import sqlite3

path = ''
db_name = 'weather.db'

# A. テーブルを作成するための関数
def init_db():
    # DB接続オブジェクトの作成
    conn = sqlite3.connect(path + db_name)
    # SQL(RDBを操作するための言語)を実行するためのカーソルオブジェクトを取得
    cur = conn.cursor()

    # テーブル作成のSQLを実行
    cur.execute('''
        CREATE TABLE IF NOT EXISTS weather_forecasts (
            area_code TEXT,
            forecast_date TEXT,
            weather_text TEXT,
            temp_max REAL,
            temp_min REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (area_code, forecast_date)
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS areas (
            area_code TEXT PRIMARY KEY,
            area_name TEXT,
            region_name TEXT
        );
    ''')

    # 変更をDBに反映させる
    conn.commit()
    # DBへの接続を閉じる
    conn.close()

# B. データを保存するための関数
def save_weather_to_db(area_code, times, weather_codes, max_temps, min_temps):
    try:
        # DB接続オブジェクトの作成
        conn = sqlite3.connect(path + db_name)
        # SQL(RDBを操作するための言語)を実行するためのカーソルオブジェクトを取得
        cur = conn.cursor()

        # データ挿入のSQLを実行
        sql = """
        INSERT OR REPLACE INTO weather_forecasts 
        (area_code, forecast_date, weather_text, temp_max, temp_min) 
        VALUES (?, ?, ?, ?, ?);
        """
        weather_data = []
        for t_val, w_code, mx, mn in zip(times, weather_codes, max_temps, min_temps):
            weather_data.append((area_code, t_val[:10], w_code, mx, mn))
        
        cur.executemany(sql, weather_data)

        # 変更をDBに反映させる
        conn.commit()

    except sqlite3.Error as e:
        print(f"エラー: {e}")

    finally:
        # DBへの接続を閉じる
        conn.close()

def fetch_weather_from_db(area_code):
    try:
        # DB接続オブジェクトの作成
        conn = sqlite3.connect(path + db_name)
        # SQL(RDBを操作するための言語)を実行するためのカーソルオブジェクトを取得
        cur = conn.cursor()

        # データ取得のSQLを実行
        sql = """
        SELECT forecast_date, weather_text, temp_max, temp_min 
        FROM weather_forecasts 
        WHERE area_code = ? 
        ORDER BY forecast_date;
        """
        cur.execute(sql, (area_code,))
        rows = cur.fetchall()
        return rows

    except sqlite3.Error as e:
        print(f"エラー: {e}")
        return []

    finally:
        # DBへの接続を閉じる
        conn.close()

    # エリア情報を保存する関数
def save_area_info(area_code, area_name, region_name):
    # DB接続オブジェクトの作成
    conn = sqlite3.connect(db_name)
    # SQL(RDBを操作するための言語)を実行するためのカーソルオブジェクトを取得
    cur = conn.cursor()

    # データ挿入のSQLを実行
    sql = "INSERT OR REPLACE INTO areas (area_code, area_name, region_name) VALUES (?, ?, ?);"
    cur.execute(sql, (area_code, area_name, region_name))

    # 変更をDBに反映させる
    conn.commit()
    # DBへの接続を閉じる
    conn.close()

# DBからエリア情報を全部取ってくる関数
def fetch_all_areas():
    # DB接続オブジェクトの作成
    conn = sqlite3.connect(db_name)
    # SQL(RDBを操作するための言語)を実行するためのカーソルオブジェクトを取得
    cur = conn.cursor()

    # データ取得のSQLを実行
    cur.execute("SELECT area_code, area_name, region_name FROM areas")
    rows = cur.fetchall()
    # DBへの接続を閉じる
    conn.close()
    return rows


def fetch_weather_by_date(area_code, target_date):
    # DB接続オブジェクトの作成
    conn = sqlite3.connect(db_name)
    # SQL(RDBを操作するための言語)を実行するためのカーソルオブジェクトを取得
    cur = conn.cursor()

    # データ取得のSQLを実行
    sql = """
    SELECT forecast_date, weather_text, temp_max, temp_min 
    FROM weather_forecasts 
    WHERE area_code = ? AND forecast_date LIKE ?
    """
    cur.execute(sql, (area_code, f"{target_date}%"))
    row = cur.fetchone() 
    # DBへの接続を閉じる
    conn.close()
    return row