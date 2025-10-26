import sqlite3
import json
from datetime import datetime, timedelta
import pytz
from collections import defaultdict
import uuid
import logging
from utils.path import get_resource_path

# 获取日志文件路径
log_path = get_resource_path("db/db_operations.log")

# 配置日志
logging.basicConfig(filename=log_path, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

db_path = get_resource_path("db/manifest.db")


def create_tables():
    conn = None
    try:
        # 连接到数据库（如果数据库不存在则创建）
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 创建主表 MainExcelTable
        cursor.execute('''CREATE TABLE IF NOT EXISTS MainExcelTable (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              sequence TEXT,
                              created_at TEXT,
                              state TEXT,
                              main_table_data TEXT,
                              deleted_at TEXT,  -- 新增：删除时间，用于软删除
                              username TEXT,      -- 新增：用户名
                              AirWayBill TEXT
                          )''')

        # 创建子表 SubExcelTable
        cursor.execute('''CREATE TABLE IF NOT EXISTS SubExcelTable (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              main_id TEXT,
                              sequence TEXT,  -- 设置为唯一的序列号，与ID相同
                              state TEXT,
                              event_time TEXT,
                              deleted_at TEXT,  -- 新增：删除时间，用于软删除
                              username TEXT,     -- 新增：用户名
                              IOSS TEXT,
                              TrackingNumber TEXT,
                              lrn, Text,
                              sub_table_data TEXT,
                              FOREIGN KEY (main_id) REFERENCES MainExcelTable (sequence)
                          )''')

        # 创建数据表 SubExcelData
        cursor.execute('''CREATE TABLE IF NOT EXISTS SubExcelData (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              sub_table_id TEXT,  -- 外键引用 SubExcelTable 的 sequence
                              row_data TEXT,
                              previous_document TEXT,      -- 手动输入字段 1（[{},{}]）
                              additional_information TEXT,  -- 手动输入字段 2（[{},{}]）
                              supporting_document TEXT,     -- 手动输入字段 3（[{},{}]）
                              additional_reference TEXT,    -- 手动输入字段 4（[{},{}]）
                              transport_document TEXT,      -- 手动输入字段 5（[{},{}]）
                              deleted_at TEXT,  -- 新增：删除时间，用于软删除
                              username TEXT,    -- 新增：用户名
                              FOREIGN KEY (sub_table_id) REFERENCES SubExcelTable (sequence)
                          )''')

        # 创建新表 SubXMLData
        cursor.execute('''CREATE TABLE IF NOT EXISTS SubXMLData (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              main_table_id TEXT,    -- 外键引用 MainExcelTable 的 sequence
                              sub_table_id TEXT,     -- 外键引用 SubExcelTable 的 sequence
                              type TEXT,             -- 类型字段
                              xml_json_data TEXT,
                              event_time TEXT,       -- 发生时间（替换 reply_received_at）
                              direction TEXT,        -- 发送或接收的标记
                              deleted_at TEXT,       -- 删除时间，用于软删除
                              username TEXT,         -- 新增：用户名,
                              CR TEXT,
                              messageID TEXT,
                              FOREIGN KEY (main_table_id) REFERENCES MainExcelTable (sequence),
                              FOREIGN KEY (sub_table_id) REFERENCES SubExcelTable (sequence)
                          )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS SignatureForm (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自增
                main_id TEXT,       --messageID这里实际是messageID
                data TEXT,
                direction TEXT,
                related_id TEXT,
                type TEXT,
                username TEXT  -- 新增：用户名
            )
        ''')

        # 创建 InputCache 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS InputCache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自增
                input_id INTEGER,
                cache_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                username TEXT  -- 新增：用户名
            )
        ''')

        # 提交事务
        conn.commit()
        print("数据库表创建成功")

    except sqlite3.DatabaseError as e:
        if conn:
            conn.rollback()  # 出现异常时回滚事务
        logging.error(f"数据库错误: {e}")
        print(f"数据库错误: {e}")
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"未知错误: {e}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()


# 存储manifest以及相关数据

def store_excel_data(main_table_data, sub_tables_data, sub_tables_additional_data, username):
    conn = None
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取波兰时间
        poland_timezone = pytz.timezone("Europe/Warsaw")
        poland_time = datetime.now(poland_timezone).strftime("%Y-%m-%d %H:%M:%S")

        # 生成 UUID 作为主表的 sequence
        main_sequence = str(uuid.uuid4())
        main_data_json = json.dumps(main_table_data)
        AirWayBill = str(sub_tables_data[0][0].get('AirWayBill', ''))

        # 插入主表数据，包含 sequence
        cursor.execute(
            '''INSERT INTO MainExcelTable 
               (created_at, state, main_table_data, username, AirWayBill, sequence) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (poland_time, "Not Sent", main_data_json, username, AirWayBill, main_sequence)
        )

        # 插入子表数据
        for sub_table_data in sub_tables_data:
            IOSS = str(sub_table_data[0].get('IOSS', ''))
            TrackingNumber = sub_table_data[0].get('TrackingNumber', '')
            sub_sequence = str(uuid.uuid4())  # 生成 UUID 作为子表的 sequence
            sub_table_json = json.dumps(main_table_data.get('goodshipment additional reference', {}))

            # 插入子表数据，包含 sequence
            cursor.execute(
                '''INSERT INTO SubExcelTable 
                   (main_id, state, event_time, username, IOSS, TrackingNumber, sub_table_data, sequence) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (main_sequence, "Not sent", None, username, IOSS, TrackingNumber, sub_table_json, sub_sequence)
            )

            # 插入子表的每行数据
            for row_data in sub_table_data:
                row_json = json.dumps(row_data)

                # 序列化附加数据
                json_previous_document = json.dumps(sub_tables_additional_data[0])
                json_additional_information = json.dumps(sub_tables_additional_data[1])
                json_supporting_document = json.dumps(sub_tables_additional_data[2])
                json_additional_reference = json.dumps(sub_tables_additional_data[3])
                json_transport_document = json.dumps(sub_tables_additional_data[4])

                cursor.execute(
                    '''INSERT INTO SubExcelData 
                       (sub_table_id, row_data, previous_document, additional_information, 
                        supporting_document, additional_reference, transport_document, username) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (sub_sequence, row_json, json_previous_document, json_additional_information,
                     json_supporting_document, json_additional_reference, json_transport_document, username)
                )

        # 提交事务
        conn.commit()
        print("Excel 数据存储成功")

    except sqlite3.DatabaseError as e:
        if conn:
            conn.rollback()  # 发生数据库异常时回滚事务
        logging.error(f"数据库错误: {e}")
        print(f"数据库错误: {e}")
    except KeyError as e:
        if conn:
            conn.rollback()
        logging.error(f"数据缺失错误: 缺少字段 {e}")
        print(f"数据缺失错误: 缺少字段 {e}")
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"未知错误: {e}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()


# 存储回复文件信息
def store_xml_data(main_table_id, sub_table_id, type_value, xml_json_data, event_time, direction, username, cr,
                   message_id):
    conn = None
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 序列化 XML JSON 数据
        xml_json_str = json.dumps(xml_json_data)

        # 插入 XML 数据到 SubXMLData 表
        cursor.execute(
            '''INSERT INTO SubXMLData 
               (main_table_id, sub_table_id, type, xml_json_data, event_time, username, direction, CR, messageID) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (main_table_id, sub_table_id, type_value, xml_json_str, event_time, username, direction, cr, message_id)
        )

        # 提交事务
        conn.commit()
        print("XML 数据存储成功")

    except sqlite3.DatabaseError as e:
        if conn:
            conn.rollback()  # 发生数据库异常时回滚事务
        logging.error(f"数据库错误: {e}")
        print(f"数据库错误: {e}")
    except json.JSONDecodeError as e:
        if conn:
            conn.rollback()
        logging.error(f"JSON 解码错误: {e}")
        print(f"JSON 解码错误: {e}")
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"未知错误: {e}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()


# 读取 MainExcelTable 中所有的信息
def get_main_table_data(username=None):
    conn = None
    main_table_data = []
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询未删除的记录，根据是否提供 username 进行筛选
        if username:
            cursor.execute(
                "SELECT * FROM MainExcelTable WHERE deleted_at IS NULL AND username = ? ORDER BY created_at DESC",
                (username,)
            )
        else:
            cursor.execute(
                "SELECT * FROM MainExcelTable WHERE deleted_at IS NULL ORDER BY created_at DESC"
            )

        # 获取查询结果
        main_table_data = cursor.fetchall()
        print("主表数据查询成功")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

    return main_table_data


# 获取所有username对应的本地数据库存在的sequence
def get_active_main_id(username):
    conn = None
    sequences = []
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询未被删除且匹配指定 username 的 sequence 值
        cursor.execute(
            "SELECT sequence FROM MainExcelTable WHERE deleted_at IS NULL AND username = ?",
            (username,)
        )

        # 提取 sequence 值列表
        sequences = [row[0] for row in cursor.fetchall()]
        print("成功获取 active main_id")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，用户名: {username}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，用户名: {username}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

    # 返回 sequence 列表
    return sequences


# 获取所有未被删除的表的id
def get_active_main_ids_state_not_sent(username=None):
    conn = None
    active_ids = []
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询未删除且状态为 'Not Sent' 的主表 ID
        if username:
            cursor.execute(
                "SELECT sequence FROM MainExcelTable WHERE deleted_at IS NULL AND state = 'Not Sent' AND username = ?",
                (username,)
            )
        else:
            cursor.execute(
                "SELECT sequence FROM MainExcelTable WHERE deleted_at IS NULL AND state = 'Not Sent'"
            )

        # 获取查询结果
        active_ids = [row[0] for row in cursor.fetchall()]
        print("成功获取状态为 'Not Sent' 的主表 ID 列表")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，用户名: {username}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，用户名: {username}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

    # 返回 active_ids 列表
    return active_ids


# 获取所有未被删除的表的id，其state是'Sent'和'Require Response'
def get_active_main_ids_state_sent_or_require_response(username=None):
    conn = None
    active_ids = []
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询未删除且状态为 'Sent' 或 'Require Response' 的主表 ID
        if username:
            cursor.execute("""
                SELECT sequence FROM MainExcelTable 
                WHERE deleted_at IS NULL 
                  AND state IN ('Sent', 'Require Response') 
                  AND username = ?
            """, (username,))
        else:
            cursor.execute("""
                SELECT sequence FROM MainExcelTable 
                WHERE deleted_at IS NULL 
                  AND state IN ('Sent', 'Require Response')
            """)

        # 获取查询结果
        active_ids = [row[0] for row in cursor.fetchall()]
        print("成功获取状态为 'Sent' 或 'Require Response' 的主表 ID 列表")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，用户名: {username}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，用户名: {username}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

    # 返回 active_ids 列表
    return active_ids


# 获取所有未被删除且状态为 'Require Response' 的主表 ID
def get_active_main_ids_state_require_response(username=None):
    conn = None
    active_ids = []
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询未删除且状态为 'Require Response' 的主表 ID
        if username:
            cursor.execute("""
                SELECT sequence FROM MainExcelTable 
                WHERE deleted_at IS NULL 
                  AND state = 'Require Response' 
                  AND username = ?
            """, (username,))
        else:
            cursor.execute("""
                SELECT sequence FROM MainExcelTable 
                WHERE deleted_at IS NULL 
                  AND state = 'Require Response'
            """)

        # 获取查询结果
        active_ids = [row[0] for row in cursor.fetchall()]
        print("成功获取状态为 'Require Response' 的主表 ID 列表")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，用户名: {username}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，用户名: {username}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

    # 返回 active_ids 列表
    return active_ids


# 根据 MainExcelTable id 获取对应 SubExcelTable 中的信息
def get_sub_tables_by_main_id(main_id, username=None):
    conn = None
    sub_table_data = []
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 根据主表 ID 和用户名查询未删除的子表记录
        if username:
            cursor.execute("""
                SELECT * FROM SubExcelTable 
                WHERE main_id = ? AND deleted_at IS NULL AND username = ?
            """, (main_id, username))
        else:
            cursor.execute("""
                SELECT * FROM SubExcelTable 
                WHERE main_id = ? AND deleted_at IS NULL
            """, (main_id,))

        # 获取查询结果
        sub_table_data = cursor.fetchall()
        print(f"成功获取主表 ID {main_id} 下的子表数据")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，主表 ID: {main_id}，用户名: {username}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，主表 ID: {main_id}，用户名: {username}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

    # 返回查询到的子表数据
    return sub_table_data


# 根据 SubExcelTable id 读取 SubExcelData 中的信息
def get_sub_table_data(sub_table_id, username=None):
    conn = None
    sub_data = []
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 根据子表 ID 和用户名查询未删除的子表数据记录
        if username:
            cursor.execute("""
                SELECT * FROM SubExcelData 
                WHERE sub_table_id = ? AND deleted_at IS NULL AND username = ?
            """, (sub_table_id, username))
        else:
            cursor.execute("""
                SELECT * FROM SubExcelData 
                WHERE sub_table_id = ? AND deleted_at IS NULL
            """, (sub_table_id,))

        # 获取查询结果
        sub_data = cursor.fetchall()
        print(f"成功获取子表 ID {sub_table_id} 的数据")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，子表 ID: {sub_table_id}，用户名: {username}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，子表 ID: {sub_table_id}，用户名: {username}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

    # 返回查询到的子表数据
    return sub_data


# 根据 sub_table_id 查询未删除的 SubXMLData 数据，并按 event_time 排序
def get_sub_xml_data_by_sub_table_id(sub_table_id, username=None):
    conn = None
    xml_data = []
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 根据子表 ID 和用户名查询未删除的 XML 数据记录，按 event_time 排序
        if username:
            cursor.execute("""
                SELECT * FROM SubXMLData 
                WHERE sub_table_id = ? AND deleted_at IS NULL AND username = ?
                ORDER BY event_time
            """, (sub_table_id, username))
        else:
            cursor.execute("""
                SELECT * FROM SubXMLData 
                WHERE sub_table_id = ? AND deleted_at IS NULL 
                ORDER BY event_time
            """, (sub_table_id,))

        # 获取查询结果
        xml_data = cursor.fetchall()
        print(f"成功获取子表 ID {sub_table_id} 的 XML 数据")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，子表 ID: {sub_table_id}，用户名: {username}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，子表 ID: {sub_table_id}，用户名: {username}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

    # 返回查询到的 XML 数据
    return xml_data


# 根据 main_table_id 查询未删除的 SubXMLData 数据，并排序
def get_sub_xml_data_by_main_table_id(main_table_id, username=None):
    conn = None
    xml_data = []
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 根据主表 ID 和用户名查询未删除的 XML 数据记录，按 sub_table_id 和 event_time 排序
        if username:
            cursor.execute("""
                SELECT * FROM SubXMLData 
                WHERE main_table_id = ? AND deleted_at IS NULL AND username = ?
                ORDER BY sub_table_id, event_time
            """, (main_table_id, username))
        else:
            cursor.execute("""
                SELECT * FROM SubXMLData 
                WHERE main_table_id = ? AND deleted_at IS NULL 
                ORDER BY sub_table_id, event_time
            """, (main_table_id,))

        # 获取查询结果
        xml_data = cursor.fetchall()
        print(f"成功获取主表 ID {main_table_id} 的 XML 数据")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，主表 ID: {main_table_id}，用户名: {username}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，主表 ID: {main_table_id}，用户名: {username}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

    # 返回查询到的 XML 数据
    return xml_data


# 根据主id修改 MainExcelTable 中的信息
def update_main_table(main_id, new_creation_time=None, new_state=None, new_data=None):
    conn = None
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 用于更新的列和值
        updates = []
        params = []

        # 根据传入的值决定更新哪些字段
        if new_creation_time is not None:
            updates.append("created_at = ?")
            params.append(new_creation_time)
        if new_state is not None:
            updates.append("state = ?")
            params.append(new_state)
        if new_data is not None:
            updates.append("main_table_data = ?")
            params.append(json.dumps(new_data))

        # 如果有需要更新的字段
        if updates:
            sql_query = f"UPDATE MainExcelTable SET {', '.join(updates)} WHERE sequence = ?"
            params.append(main_id)

            # 执行更新操作
            cursor.execute(sql_query, params)
            conn.commit()
            logging.info(f"主表 ID {main_id} 更新成功：{', '.join(updates)}")
        else:
            logging.warning(f"未提供任何更新字段，主表 ID {main_id} 未进行任何更新操作。")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，主表 ID: {main_id}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，主表 ID: {main_id}")
        print(f"未知错误: {e}")
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 根据主id修改 SubExcelTable 中的信息
def update_sub_table(sub_id, new_main_id=None, new_event_time=None, new_state=None,
                     new_deleted_at=None, new_username=None, new_IOSS=None,
                     new_TrackingNumber=None, new_lrn=None, new_sub_table_data=None):
    conn = None
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 用于更新的列和值
        updates = []
        params = []

        # 根据传入的值决定更新哪些字段
        if new_main_id is not None:
            updates.append("main_id = ?")
            params.append(new_main_id)
        if new_event_time is not None:
            updates.append("event_time = ?")
            params.append(new_event_time)
        if new_state is not None:
            updates.append("state = ?")
            params.append(new_state)
        if new_deleted_at is not None:
            updates.append("deleted_at = ?")
            params.append(new_deleted_at)
        if new_username is not None:
            updates.append("username = ?")
            params.append(new_username)
        if new_IOSS is not None:
            updates.append("IOSS = ?")
            params.append(new_IOSS)
        if new_TrackingNumber is not None:
            updates.append("TrackingNumber = ?")
            params.append(new_TrackingNumber)
        if new_lrn is not None:
            updates.append("lrn = ?")
            params.append(new_lrn)
        if new_sub_table_data is not None:
            updates.append("sub_table_data = ?")
            params.append(json.dumps(new_sub_table_data))

        # 如果有需要更新的字段
        if updates:
            sql_query = f"UPDATE SubExcelTable SET {', '.join(updates)} WHERE sequence = ?"
            params.append(sub_id)

            # 执行更新操作
            cursor.execute(sql_query, params)
            conn.commit()
            logging.info(f"子表 ID {sub_id} 更新成功：{', '.join(updates)}")
        else:
            logging.warning(f"未提供任何更新字段，子表 ID {sub_id} 未进行任何更新操作。")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，子表 ID: {sub_id}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，子表 ID: {sub_id}")
        print(f"未知错误: {e}")
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 根据主id修改 SubExcelData 中的信息
def update_sub_table_data(sub_data_id, new_sub_table_id=None, new_data=None,
                          previous_document=None, additional_information=None,
                          supporting_document=None, additional_reference=None,
                          transport_document=None):
    conn = None
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 用于更新的列和值
        updates = []
        params = []

        # 更新 sub_table_id
        if new_sub_table_id is not None:
            updates.append("sub_table_id = ?")
            params.append(new_sub_table_id)

        # 更新 row_data
        if new_data is not None:
            updates.append("row_data = ?")
            params.append(json.dumps(new_data))  # 确保 new_data 被序列化为 JSON 字符串

        # 更新 5 个手动输入字段
        if previous_document is not None:
            updates.append("previous_document = ?")
            params.append(json.dumps(previous_document))  # 序列化为 JSON 字符串
        if additional_information is not None:
            updates.append("additional_information = ?")
            params.append(json.dumps(additional_information))  # 序列化为 JSON 字符串
        if supporting_document is not None:
            updates.append("supporting_document = ?")
            params.append(json.dumps(supporting_document))  # 序列化为 JSON 字符串
        if additional_reference is not None:
            updates.append("additional_reference = ?")
            params.append(json.dumps(additional_reference))  # 序列化为 JSON 字符串
        if transport_document is not None:
            updates.append("transport_document = ?")
            params.append(json.dumps(transport_document))  # 序列化为 JSON 字符串

        # 如果有任何更新项
        if updates:
            sql_query = f"UPDATE SubExcelData SET {', '.join(updates)} WHERE sub_table_id = ?"
            params.append(sub_data_id)

            # 执行更新操作
            cursor.execute(sql_query, params)
            conn.commit()
            logging.info(f"子表数据 ID {sub_data_id} 更新成功：{', '.join(updates)}")
        else:
            logging.warning(f"未提供任何更新字段，子表数据 ID {sub_data_id} 未进行任何更新操作。")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，子表数据 ID: {sub_data_id}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，子表数据 ID: {sub_data_id}")
        print(f"未知错误: {e}")
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 软删除 MainExcelTable 中的信息
def soft_delete(table_name, record_id):
    conn = None
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取当前时间（波兰时区）
        delete_time = datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M:%S")

        # 确保表名和记录 ID 有效
        if not table_name or not record_id:
            raise ValueError("Invalid table name or record ID")

        # 执行软删除操作
        cursor.execute(f"UPDATE {table_name} SET deleted_at = ? WHERE sequence = ?", (delete_time, record_id))

        # 提交事务
        conn.commit()

        # 记录删除操作
        logging.info(f"软删除操作：表名 {table_name}, 记录 ID {record_id}, 删除时间 {delete_time}")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，表名: {table_name}, 记录 ID: {record_id}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，表名: {table_name}, 记录 ID: {record_id}")
        print(f"未知错误: {e}")
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 根据 main_id 删除所有相关记录
def soft_delete_all_related(main_id):
    conn = None
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取当前时间（波兰时区）
        delete_time = datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M:%S")

        # 软删除 MainExcelTable 中的记录
        cursor.execute("UPDATE MainExcelTable SET deleted_at = ? WHERE sequence = ?", (delete_time, main_id))

        # 软删除与 main_id 相关的 SubExcelTable 中的记录
        cursor.execute("UPDATE SubExcelTable SET deleted_at = ? WHERE main_id = ?", (delete_time, main_id))

        # 获取与 main_id 相关的所有 SubExcelTable 的 id
        cursor.execute("SELECT sequence FROM SubExcelTable WHERE main_id = ?", (main_id,))
        sub_table_ids = cursor.fetchall()

        # 软删除 SubExcelData 和 SubXMLData 中与 sub_table_ids 相关的记录
        for sub_table_id in sub_table_ids:
            sub_id = sub_table_id[0]
            cursor.execute("UPDATE SubExcelData SET deleted_at = ? WHERE sub_table_id = ?", (delete_time, sub_id))
            cursor.execute("UPDATE SubXMLData SET deleted_at = ? WHERE sub_table_id = ?", (delete_time, sub_id))

        # 提交事务
        conn.commit()

        # 记录删除操作
        logging.info(f"软删除操作：主表 ID {main_id} 及其关联的子表记录已删除，删除时间 {delete_time}")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，主表 ID: {main_id}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，主表 ID: {main_id}")
        print(f"未知错误: {e}")
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


def update_all_by_sub_table_id(sub_table_id, field_name, new_value):
    """
    根据 sub_table_id 批量更新 SubExcelData 表中某一个手动输入字段的值。

    参数:
    - sub_table_id (int): 要更新的 sub_table_id。
    - field_name (str): 要更新的字段名称（例如 'previous_document'、'additional_information' 等）。
    - new_value (list): 新的字段值，建议为列表或可序列化为 JSON 的对象。

    返回:
    - None
    """
    # 检查字段名是否合法
    valid_fields = ["previous_document", "additional_information",
                    "supporting_document", "additional_reference",
                    "transport_document"]

    if field_name not in valid_fields:
        raise ValueError(f"非法字段名: {field_name}. 请使用以下字段之一: {', '.join(valid_fields)}")

    conn = None  # 定义连接对象，方便在 finally 中关闭
    try:
        # 连接数据库并更新字段
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 将 new_value 序列化为 JSON 字符串
        json_value = json.dumps(new_value)

        # 构建 SQL 查询
        sql_query = f"UPDATE SubExcelData SET {field_name} = ? WHERE sub_table_id = ?"
        cursor.execute(sql_query, (json_value, sub_table_id))

        # 提交事务
        conn.commit()

        # 记录日志
        logging.info(f"更新成功：sub_table_id={sub_table_id}, 字段={field_name}, 新值={new_value}")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，sub_table_id: {sub_table_id}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，sub_table_id: {sub_table_id}")
        print(f"未知错误: {e}")
    finally:
        # 确保数据库连接被关闭
        if conn:
            conn.close()


def insert_into_input_cache(input_id, cache_data, username):
    """
    向 InputCache 表插入一条记录。

    :param input_id: 输入框 ID
    :param cache_data: JSON 格式的数据，字符串形式
    :param username: 用户名
    """
    db_name = db_path
    conn = None  # 定义连接对象，方便在 finally 中关闭

    # 验证 cache_data 是否可以被序列化为 JSON
    try:
        json_data = json.dumps(cache_data)  # 尝试将数据转换为 JSON 字符串
    except (TypeError, ValueError) as e:
        logging.error(f"无效的 JSON 数据: {cache_data}. 错误: {e}")
        raise ValueError(f"无效的 cache_data 数据: {cache_data}. 必须是可序列化为 JSON 的数据结构。")

    try:
        # 连接数据库
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # 插入数据
        cursor.execute('''
        INSERT INTO InputCache (input_id, cache_data, username) 
        VALUES (?, ?, ?)
        ''', (input_id, json_data, username))  # 将 cache_data 转换为 JSON 字符串

        # 提交事务
        conn.commit()

        # 记录成功日志（避免记录过多的敏感数据，记录前100字符）
        logging.info(f"成功插入记录: input_id={input_id}, username={username}, cache_data={json_data[:100]}...")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，插入记录失败，input_id: {input_id}, username: {username}")
        raise  # 重新抛出异常
    except Exception as e:
        logging.error(f"未知错误: {e}，插入记录失败，input_id: {input_id}, username: {username}")
        raise  # 重新抛出异常
    finally:
        # 关闭连接，确保资源释放
        if conn:
            conn.close()


def update_cache_data(input_id, new_cache_data):
    """
    根据 input_id 更新 InputCache 表中的 cache_data。

    :param input_id: 输入框 ID
    :param new_cache_data: 新的 JSON 格式的数据，字符串形式
    """
    db_name = db_path
    conn = None

    try:
        # 创建数据库连接
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # 更新 cache_data
        cursor.execute('''
        UPDATE InputCache 
        SET cache_data = ? 
        WHERE input_id = ?
        ''', (json.dumps(new_cache_data), input_id))  # 将新数据转换为 JSON 字符串

        # 提交更改
        conn.commit()

        # 记录日志：操作成功
        logging.info(f"成功更新输入框 {input_id} 的 cache_data。")

    except sqlite3.Error as e:
        # 捕获数据库操作异常
        logging.error(f"数据库操作错误: {e}, 输入框 ID: {input_id}")
        conn.rollback()  # 如果发生错误，回滚事务

    except Exception as e:
        # 捕获其他类型的异常
        logging.error(f"未知错误: {e}, 输入框 ID: {input_id}")

    finally:
        # 确保关闭数据库连接
        if conn:
            conn.close()


def get_input_cache_data(input_id, username):
    """
    根据 input_id 获取 InputCache 表中的数据的 cache_data，并返回 JSON 格式。

    :param input_id: 输入框 ID
    :param username: 用户名
    :return: 返回对应的 cache_data JSON 数据
    """
    db_name = db_path
    conn = None
    try:
        # 创建数据库连接
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        if input_id is not None:
            query = 'SELECT cache_data FROM InputCache WHERE input_id = ? AND username = ?'
            parameters = (input_id, username)
        else:
            raise ValueError("必须提供 input_id。")

        cursor.execute(query, parameters)
        rows = cursor.fetchall()

        # 处理查询结果
        if rows:
            logging.info(f"成功获取 input_id = {input_id} 用户 {username} 的 cache_data 数据。")
            return json.loads(rows[0][0])  # 返回第一个结果的字典
        else:
            logging.info(f"没有找到 input_id = {input_id} 用户 {username} 的 cache_data 数据。")
            return []  # 如果没有结果，则返回空列表

    except sqlite3.Error as e:
        # 捕获数据库操作异常
        logging.error(f"数据库操作错误: {e}, 输入框 ID: {input_id}, 用户名: {username}")
        return None

    except ValueError as ve:
        # 捕获传入参数异常
        logging.error(f"参数错误: {ve}, 输入框 ID: {input_id}, 用户名: {username}")
        return None

    except Exception as e:
        # 捕获其他类型的异常
        logging.error(f"未知错误: {e}, 输入框 ID: {input_id}, 用户名: {username}")
        return None

    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


def fetch_all_from_input_cache(username):
    """
    获取所有与指定用户名相关的 InputCache 数据。

    :param username: 用户名
    :return: 返回与用户名相关的所有缓存数据
    """
    db_name = db_path  # 数据库路径
    conn = None
    try:
        # 创建数据库连接
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # 执行查询所有与指定用户名相关的值的 SQL 语句
        cursor.execute('SELECT * FROM InputCache WHERE username = ?', (username,))

        # 获取所有结果
        rows = cursor.fetchall()

        logging.info(f"成功获取用户名为 {username} 的所有 InputCache 数据。")
        return rows

    except sqlite3.Error as e:
        # 捕获数据库操作异常
        logging.error(f"数据库操作错误: {e}, 用户名: {username}")
        return None

    except Exception as e:
        # 捕获其他类型的异常
        logging.error(f"未知错误: {e}, 用户名: {username}")
        return None

    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


def fetch_zc415_data_by_main_id(main_id):
    """
    根据 main_id 获取与之相关的所有数据（包括 MainExcelTable 和 SubExcelTable 数据）。

    :param main_id: 主表 ID
    :return: 包含 main_table_data 和相关 sub_data 的字典
    """
    db_name = db_path
    connection = None
    cursor = None

    try:
        # 连接到数据库
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        # 查询 MainExcelTable 中的 main_table_data
        cursor.execute("SELECT main_table_data FROM MainExcelTable WHERE sequence = ?", (main_id,))
        main_data = cursor.fetchone()

        if not main_data:
            logging.warning(f"No data found for MainExcelTable ID: {main_id}")
            return None

        main_table_data = main_data[0]
        main_table_data_json = json.loads(main_table_data)  # 转为 JSON 格式

        # 查询 SubExcelTable 中与 main_id 相关的所有子表 id
        cursor.execute("SELECT sequence FROM SubExcelTable WHERE main_id = ?", (main_id,))
        sub_ids = [row[0] for row in cursor.fetchall()]  # 提取所有子表的 id

        # 使用 defaultdict 来存储 SubExcelData，按 sub_id 分组
        sub_data_dict = defaultdict(list)

        # 查询 SubExcelData 中与每个子表 id 相关的所有数据
        for sub_id in sub_ids:
            cursor.execute(
                "SELECT row_data, previous_document, additional_information, supporting_document, additional_reference, transport_document "
                "FROM SubExcelData WHERE sub_table_id = ?",
                (sub_id,))
            for row in cursor.fetchall():
                row_data, previous_document, additional_information, supporting_document, additional_reference, transport_document = row

                # 转换为 JSON 格式
                row_data_json = json.loads(row_data)
                previous_document_json = json.loads(previous_document)
                additional_information_json = json.loads(additional_information)
                supporting_document_json = json.loads(supporting_document)
                additional_reference_json = json.loads(additional_reference)
                transport_document_json = json.loads(transport_document)

                # 将数据组合成一个字典
                combined_data = {
                    "row_data": row_data_json,
                    "previous_document": previous_document_json,
                    "additional_information": additional_information_json,
                    "supporting_document": supporting_document_json,
                    "additional_reference": additional_reference_json,
                    "transport_document": transport_document_json,
                }

                # 将数据添加到对应的 sub_id 列表中
                sub_data_dict[sub_id].append(combined_data)

        # 转换 defaultdict 为普通列表格式
        sub_data_list = [{"sub_id": sub_id, "rows_data": data} for sub_id, data in sub_data_dict.items()]

        # 返回所有提取的数据
        result = {
            "main_id": main_id,
            "main_table_data": main_table_data_json,
            "sub_data": sub_data_list,
        }

        logging.info(f"成功获取 MainExcelTable ID: {main_id} 的相关数据。")
        return result

    except sqlite3.Error as e:
        logging.error(f"数据库操作错误: {e}, MainExcelTable ID: {main_id}")
        return None

    except json.JSONDecodeError as e:
        logging.error(f"JSON 解码错误: {e}, MainExcelTable ID: {main_id}")
        return None

    except Exception as e:
        logging.error(f"未知错误: {e}, MainExcelTable ID: {main_id}")
        return None

    finally:
        # 确保数据库连接关闭
        if connection:
            connection.close()


# 这里需要做一些修改
# 发送消息成功后调用的函数，将main_id对应的主表和子表中的state都改成Sent
def update_state_to_sent(main_id):
    """
    将 MainExcelTable 和 SubExcelTable 中与指定 main_id 相关的记录的 state 更新为 'Sent'。

    :param main_id: 主表 ID
    """
    db_name = db_path
    connection = None
    cursor = None

    try:
        # 创建数据库连接
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        # 开始事务
        connection.execute("BEGIN")

        # 更新 MainExcelTable 中的 state 为 'Sent'
        cursor.execute('''
            UPDATE MainExcelTable
            SET state = 'Sent'
            WHERE sequence = ?
        ''', (main_id,))
        logging.info(f"成功更新 MainExcelTable 中的 state 为 'Sent', main_id: {main_id}")

        # 更新 SubExcelTable 中所有对应的 state 为 'Sent'
        cursor.execute('''
            UPDATE SubExcelTable
            SET state = 'Sent'
            WHERE main_id = ?
        ''', (main_id,))
        logging.info(f"成功更新 SubExcelTable 中的 state 为 'Sent', main_id: {main_id}")

        # 提交事务
        connection.commit()
        logging.info(f"成功提交事务，main_id: {main_id}")

    except sqlite3.Error as e:
        # 出现数据库错误时回滚事务
        if connection:
            connection.rollback()
        logging.error(f"数据库错误: {e}, main_id: {main_id}")
    except Exception as e:
        # 捕获其他异常并回滚事务
        if connection:
            connection.rollback()
        logging.error(f"未知错误: {e}, main_id: {main_id}")
    finally:
        # 确保数据库连接关闭
        if connection:
            connection.close()


# 根据id和用户名查询主表中是否有存在
def check_id_from_main_table(id, username):
    """
    检查 MainExcelTable 中是否存在指定 id 和 username，并且未被软删除。

    :param id: 记录的 ID
    :param username: 用户名
    :return: 如果记录存在并未被软删除，返回 True；否则返回 False
    """
    conn = None
    cursor = None

    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询是否存在指定 id 和 username 且未被软删除
        query = '''
            SELECT 1 FROM MainExcelTable
            WHERE sequence = ? AND username = ? AND deleted_at IS NULL
            LIMIT 1;
        '''
        cursor.execute(query, (id, username))
        result = cursor.fetchone()

        if result:
            logging.info(f"成功查询到 MainExcelTable 中的记录，ID: {id}, 用户名: {username}")
        else:
            logging.info(f"未在 MainExcelTable 中找到指定记录，ID: {id}, 用户名: {username}")

        return result is not None

    except sqlite3.Error as e:
        # 捕获数据库错误并记录日志
        logging.error(f"数据库错误: {e}, ID: {id}, 用户名: {username}")
        return False

    except Exception as e:
        # 捕获其他未知错误并记录日志
        logging.error(f"未知错误: {e}, ID: {id}, 用户名: {username}")
        return False

    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 根据id和用户名查询子表中是否有存在
def check_id_from_sub_table(id, username):
    """
    检查 SubExcelTable 中是否存在指定 id 和 username，并且未被软删除。

    :param id: 记录的 ID
    :param username: 用户名
    :return: 如果记录存在并未被软删除，返回 True；否则返回 False
    """
    conn = None
    cursor = None

    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询是否存在指定 id 和 username 且未被软删除
        query = '''
            SELECT 1 FROM SubExcelTable
            WHERE sequence = ? AND username = ? AND deleted_at IS NULL
            LIMIT 1;
        '''
        cursor.execute(query, (id, username))
        result = cursor.fetchone()

        if result:
            logging.info(f"成功查询到 SubExcelTable 中的记录，ID: {id}, 用户名: {username}")
        else:
            logging.info(f"未在 SubExcelTable 中找到指定记录，ID: {id}, 用户名: {username}")

        return result is not None

    except sqlite3.Error as e:
        # 捕获数据库错误并记录日志
        logging.error(f"数据库错误: {e}, ID: {id}, 用户名: {username}")
        return False

    except Exception as e:
        # 捕获其他未知错误并记录日志
        logging.error(f"未知错误: {e}, ID: {id}, 用户名: {username}")
        return False

    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


def check_id_and_state_from_main_table(id, username, state):
    """
    检查 MainExcelTable 中是否存在指定 id、username 和 state，并且未被软删除。

    :param id: 记录的 ID
    :param username: 用户名
    :param state: 目标状态
    :return: 如果记录存在且状态匹配且未被软删除，返回 True；否则返回 False
    """
    conn = None
    cursor = None

    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询是否存在指定 id、username 和 state 且未被软删除
        query = '''
            SELECT 1 FROM MainExcelTable
            WHERE sequence = ? AND username = ? AND state = ? AND deleted_at IS NULL
            LIMIT 1;
        '''
        cursor.execute(query, (id, username, state))
        result = cursor.fetchone()

        if result:
            logging.info(f"成功查询到 MainExcelTable 中的记录，ID: {id}, 用户名: {username}, 状态: {state}")
        else:
            logging.info(f"未在 MainExcelTable 中找到指定记录，ID: {id}, 用户名: {username}, 状态: {state}")

        return result is not None

    except sqlite3.Error as e:
        # 捕获数据库错误并记录日志
        logging.error(f"数据库错误: {e}, ID: {id}, 用户名: {username}, 状态: {state}")
        return False

    except Exception as e:
        # 捕获其他未知错误并记录日志
        logging.error(f"未知错误: {e}, ID: {id}, 用户名: {username}, 状态: {state}")
        return False

    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 根据main_table_id查找所有sub_table_id，并返回一个不重复的列表
def get_unique_sub_table_ids_by_main_table_id(main_table_id):
    """
    根据 MainTable ID 获取与之关联的所有不重复的 SubTable ID。

    :param main_table_id: MainExcelTable 的 ID
    :return: 返回与给定 main_table_id 关联的所有唯一的 sub_table_id 列表
    """
    conn = None
    cursor = None
    unique_sub_table_ids = []

    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询所有不重复的 sub_table_id
        cursor.execute("""
            SELECT DISTINCT sub_table_id 
            FROM SubXMLData 
            WHERE main_table_id = ? AND deleted_at IS NULL
        """, (main_table_id,))

        # 提取所有不重复的 sub_table_id 到列表
        unique_sub_table_ids = [row[0] for row in cursor.fetchall()]

        logging.info(f"成功获取 MainTable ID {main_table_id} 关联的唯一 SubTable IDs: {unique_sub_table_ids}")

    except sqlite3.Error as e:
        # 捕获数据库错误并记录日志
        logging.error(f"数据库错误: {e}, MainTable ID: {main_table_id}")
    except Exception as e:
        # 捕获其他未知错误并记录日志
        logging.error(f"未知错误: {e}, MainTable ID: {main_table_id}")
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()

    return unique_sub_table_ids


# 根据sub_table_id去查询SubXMLData中的流程信息并且排序，返回一个types列表，这个列表就是报关流程
def get_sorted_types_by_sub_table_id(sub_table_id):
    """
    根据 SubTable ID 获取所有类型，并按事件时间排序。

    :param sub_table_id: SubExcelTable 的 ID
    :return: 返回按事件时间排序的类型列表
    """
    conn = None
    cursor = None
    types = []

    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 执行查询以获取类型并按事件时间排序
        cursor.execute('''
            SELECT type
            FROM SubXMLData
            WHERE deleted_at IS NULL  -- 只获取未删除的数据
            AND sub_table_id = ?      -- 根据 sub_table_id 进行过滤
            ORDER BY event_time ASC
        ''', (sub_table_id,))

        # 获取所有类型
        types = [row[0] for row in cursor.fetchall()]

        # 记录日志
        logging.info(f"成功获取 SubTable ID {sub_table_id} 的类型: {types}")

    except sqlite3.Error as e:
        # 捕获数据库错误并记录日志
        logging.error(f"数据库错误: {e}, SubTable ID: {sub_table_id}")
    except Exception as e:
        # 捕获其他未知错误并记录日志
        logging.error(f"未知错误: {e}, SubTable ID: {sub_table_id}")
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()

    return types  # 即使发生异常，也返回空列表或查询到的类型


# 根据SubExcelTable中的main_id，查询这个报关单的申报流程中的进度，如果有Require Response那就是整个报关单需要回复。
# 如果没有Require Response但是能查询到Sent那就还没有收到回复消息。
def check_state_by_main_id(main_id, target_state):
    """
    检查指定 main_id 是否存在，并且其对应的状态为目标状态。

    :param main_id: 主表 ID
    :param target_state: 目标状态
    :return: 如果状态匹配，返回 True；否则返回 False
    """
    conn = None
    cursor = None
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 执行查询
        query = '''
            SELECT 1 FROM SubExcelTable 
            WHERE main_id = ? 
              AND state = ? 
              AND deleted_at IS NULL 
            LIMIT 1
        '''
        cursor.execute(query, (main_id, target_state))
        result = cursor.fetchone()

        # 记录查询结果
        if result:
            logging.info(f"主表 ID {main_id} 的状态已匹配为 '{target_state}'。")
        else:
            logging.info(f"主表 ID {main_id} 的状态未匹配为 '{target_state}'。")

        return result is not None
    except sqlite3.Error as e:
        # 捕获数据库错误并记录日志
        logging.error(f"数据库错误: {e}, main_id: {main_id}, target_state: {target_state}")
        return False
    except Exception as e:
        # 捕获其他未知错误并记录日志
        logging.error(f"未知错误: {e}, main_id: {main_id}, target_state: {target_state}")
        return False
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 插入 MainExcelTable 数据
def insert_main_excel_table(main_excel_data):
    """
    将主表数据插入到 MainExcelTable 中，如果记录已存在，则替换。

    :param main_excel_data: 包含要插入的主表数据的列表，每个元素是一个字典
    """
    conn = None
    cursor = None
    try:
        # 创建数据库连接
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 插入或替换数据
        for item in main_excel_data:
            cursor.execute('''
                INSERT OR REPLACE INTO MainExcelTable 
                (sequence, created_at, state, main_table_data, deleted_at, username, AirWayBill)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['sequence'], item['created_at'], item['state'], item['main_table_data'],
                item['deleted_at'], item['username'], item['AirWayBill']
            ))

        # 提交事务
        conn.commit()
        logging.info(f"成功插入 {len(main_excel_data)} 条主表数据。")
    except sqlite3.Error as e:
        # 捕获数据库相关错误
        logging.error(f"数据库错误: {e}")
    except Exception as e:
        # 捕获其他未知错误
        logging.error(f"插入主表数据时发生错误: {e}")
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 插入 SubExcelTable 数据
def insert_sub_excel_table(sub_excel_data):
    """
    将子表数据插入到 SubExcelTable 中，如果记录已存在，则替换。

    :param sub_excel_data: 包含要插入的子表数据的列表，每个元素是一个字典
    """
    conn = None
    cursor = None
    try:
        # 创建数据库连接
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 插入或替换数据
        for item in sub_excel_data:
            cursor.execute('''
                INSERT OR REPLACE INTO SubExcelTable 
                (main_id, sequence, state, event_time, deleted_at, username, IOSS, TrackingNumber, sub_table_data, lrn)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['main_id'], item['sequence'], item['state'], item['event_time'],
                item['deleted_at'], item['username'], item['IOSS'], item['TrackingNumber'],
                item['sub_table_data'], item['lrn']
            ))

        # 提交事务
        conn.commit()
        logging.info(f"成功插入 {len(sub_excel_data)} 条子表数据。")
    except sqlite3.Error as e:
        # 捕获数据库相关错误
        logging.error(f"数据库错误: {e}")
    except Exception as e:
        # 捕获其他未知错误
        logging.error(f"插入子表数据时发生错误: {e}")
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 插入 SubExcelData 数据
def insert_sub_excel_data(sub_excel_data):
    """
    将子表数据插入到 SubExcelData 中，如果记录已存在，则替换。

    :param sub_excel_data: 包含要插入的子表数据的列表，每个元素是一个字典
    """
    conn = None
    cursor = None
    try:
        # 创建数据库连接
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 插入或替换数据
        for item in sub_excel_data:
            cursor.execute('''
                INSERT OR REPLACE INTO SubExcelData 
                (sub_table_id, row_data, previous_document, additional_information, 
                 supporting_document, additional_reference, transport_document, 
                 deleted_at, username)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['sub_table_id'], item['row_data'], item['previous_document'],
                item['additional_information'], item['supporting_document'],
                item['additional_reference'], item['transport_document'],
                item['deleted_at'], item['username']
            ))

        # 提交事务
        conn.commit()
        logging.info(f"成功插入 {len(sub_excel_data)} 条子表数据。")
    except sqlite3.Error as e:
        # 捕获数据库相关错误
        logging.error(f"数据库错误: {e}")
    except Exception as e:
        # 捕获其他未知错误
        logging.error(f"插入子表数据时发生错误: {e}")
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 插入 SubXMLData 数据
def insert_sub_xml_data(sub_xml_data, username):
    """
    将子表 XML 数据插入到 SubXMLData 中，如果记录已存在则替换；
    对于 type 为 "upd" 的数据，避免插入重复记录。

    :param sub_xml_data: 包含要插入的子表 XML 数据的列表，每个元素是一个字典
    :param username: 用户名，关联到数据记录
    """
    conn = None
    cursor = None
    try:
        # 创建数据库连接
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 插入或替换数据
        for item in sub_xml_data:
            # 提取数据字段
            main_id = item.get('main_id')
            sub_id = item.get('sub_id')
            record_type = item.get('type')
            json_data = json.dumps(item.get('json_data', {}))  # 默认为空字典
            event_time = item.get('event_time')
            direction = item.get('direction')
            cr = item.get('CR', None)
            message_id = item.get('messageID', None)

            # 如果 type 是 "upd"，检查是否已有重复记录
            if record_type in ["upd", "zc429", "zcx03", "zcx64", "zcx65", "zc410", "zc460"]:
                cursor.execute('''
                    SELECT COUNT(*) FROM SubXMLData 
                    WHERE main_table_id = ? AND sub_table_id = ? AND type = ? AND username = ? AND direction = ?
                ''', (main_id, sub_id, record_type, username, direction))
                existing_count = cursor.fetchone()[0]

                # 如果存在重复记录，跳过插入
                if existing_count > 0:
                    print(f"记录已存在，跳过插入: main_id={main_id}, sub_id={sub_id}, type={record_type}")
                    continue

            # 插入或替换记录
            cursor.execute('''
                            INSERT OR REPLACE INTO SubXMLData 
                            (main_table_id, sub_table_id, type, xml_json_data, event_time,
                             direction, username, CR, messageID)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (main_id, sub_id, record_type, json_data, event_time, direction, username, cr, message_id))

        # 提交事务
        conn.commit()
        print(f"成功插入 {len(sub_xml_data)} 条子表 XML 数据。")
        logging.info(f"成功插入 {len(sub_xml_data)} 条子表 XML 数据。")
    except sqlite3.Error as e:
        # 捕获数据库相关错误
        logging.error(f"数据库错误: {e}")
        print(f"数据库错误: {e}")
    except Exception as e:
        # 捕获其他未知错误
        logging.error(f"插入子表 XML 数据时发生错误: {e}")
        print(f"插入子表 XML 数据时发生错误: {e}")
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


def get_id_and_airwaybill_from_main_table_by_state_sent(username):
    """
    获取指定用户名且状态为 'Sent' 的 MainExcelTable 中的 sequence 和 AirWayBill。

    :param username: 用户名
    :return: 返回包含两个列表：[sequence, AirWayBill]
    """
    conn = None
    cursor = None
    try:
        # 创建数据库连接
        conn = sqlite3.connect(db_path)  # 替换为您的数据库路径
        cursor = conn.cursor()

        # 执行查询，获取 sequence 和 AirWayBill
        cursor.execute('''
            SELECT sequence, AirWayBill 
            FROM MainExcelTable 
            WHERE username = ? AND state = 'Sent' AND deleted_at IS NULL
            ORDER BY created_at DESC
        ''', (username,))

        # 提取查询结果
        sequences = []
        airway_bills = []

        for row in cursor.fetchall():
            sequences.append(row[0])  # sequence
            airway_bills.append(row[1])  # AirWayBill

        logging.info(f"成功获取用户名为 {username} 的 'Sent' 状态的记录，序列号数：{len(sequences)}")

        return [sequences, airway_bills]
    except sqlite3.Error as e:
        # 捕获数据库相关错误
        logging.error(f"数据库错误: {e}")
        return None
    except Exception as e:
        # 捕获其他未知错误
        logging.error(f"获取数据时发生错误: {e}")
        return None
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


def get_id_and_airwaybill_from_main_table_by_state_not_sent(username):
    """
    获取指定用户名且状态为 'Not Sent' 的 MainExcelTable 中的 sequence 和 AirWayBill。

    :param username: 用户名
    :return: 返回包含两个列表：[sequence, AirWayBill]
    """
    conn = None
    cursor = None
    try:
        # 创建数据库连接
        conn = sqlite3.connect(db_path)  # 替换为您的数据库路径
        cursor = conn.cursor()

        # 执行查询，获取 sequence 和 AirWayBill
        cursor.execute('''
            SELECT sequence, AirWayBill 
            FROM MainExcelTable 
            WHERE username = ? AND state = 'Not Sent' AND deleted_at IS NULL
            ORDER BY created_at DESC
        ''', (username,))

        # 提取查询结果
        sequences = []
        airway_bills = []

        for row in cursor.fetchall():
            sequences.append(row[0])  # sequence
            airway_bills.append(row[1])  # AirWayBill

        logging.info(f"成功获取用户名为 {username} 的 'Not Sent' 状态的记录，序列号数：{len(sequences)}")

        return [sequences, airway_bills]
    except sqlite3.Error as e:
        # 捕获数据库相关错误
        logging.error(f"数据库错误: {e}")
        return None
    except Exception as e:
        # 捕获其他未知错误
        logging.error(f"获取数据时发生错误: {e}")
        return None
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 通过main_id获取子表IOSS和TrackingNumber
def get_id_ioss_tracking_number_by_main_id(main_ids):
    """
    获取与给定 main_ids 相关的 sequence, IOSS 和 TrackingNumber。

    :param main_ids: 由 main_id 组成的列表
    :return: 返回包含三个列表：[sequence_list, ioss_list, tracking_number_list]
    """
    conn = None
    cursor = None
    try:
        # 连接到 SQLite 数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 构造占位符字符串，数量与 main_ids 列表长度相同
        placeholders = ', '.join('?' for _ in main_ids)

        # 查询 sequence, IOSS 和 TrackingNumber
        cursor.execute(f'''
            SELECT sequence, IOSS, TrackingNumber 
            FROM SubExcelTable 
            WHERE main_id IN ({placeholders})
        ''', main_ids)

        # 获取查询结果
        results = cursor.fetchall()

        # 分别存储到三个列表中
        sequence_list = []
        ioss_list = []
        tracking_number_list = []

        for row in results:
            sequence_list.append(row[0])  # 第一个字段 sequence
            ioss_list.append(row[1])  # 第二个字段 IOSS
            tracking_number_list.append(row[2])  # 第三个字段 TrackingNumber

        logging.info(f"成功获取 {len(results)} 条数据，main_ids: {main_ids}")

        # 返回打包的列表
        return [sequence_list, ioss_list, tracking_number_list]
    except sqlite3.Error as e:
        # 捕获数据库相关错误
        logging.error(f"数据库错误: {e}")
        return None
    except Exception as e:
        # 捕获其他未知错误
        logging.error(f"发生未知错误: {e}")
        return None
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 发送zc415的时候同步MainExcelTable，SubExcelTable和SubExcelData三个数据表的数据到服务器
def fetch_data_of_send_zc415(main_id, username):
    """
    从多个表格中获取数据：MainExcelTable, SubExcelTable, SubExcelData。
    :param main_id: 主表的 ID
    :param username: 用户名
    :return: 包含数据的字典 {"MainExcelTable": [], "SubExcelTable": [], "SubExcelData": []}
    """
    conn = None
    cursor = None
    try:
        # 连接到 SQLite 数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询 MainExcelTable 数据
        main_table_data = []
        cursor.execute('''
            SELECT * FROM MainExcelTable 
            WHERE sequence = ? AND username = ?
        ''', (main_id, username))
        main_rows = cursor.fetchall()
        for row in main_rows:
            main_dict = {description[0]: row[i] for i, description in enumerate(cursor.description)}
            main_table_data.append(main_dict)

        # 查询 SubExcelTable 数据
        sub_table_data = []
        cursor.execute('''
            SELECT * FROM SubExcelTable 
            WHERE main_id = ? AND username = ?
        ''', (main_id, username))
        sub_rows = cursor.fetchall()
        for row in sub_rows:
            sub_dict = {description[0]: row[i] for i, description in enumerate(cursor.description)}
            sub_table_data.append(sub_dict)

        # 查询 SubExcelData 数据
        sub_excel_data = []
        for sub in sub_table_data:
            sub_sequence = sub["sequence"]
            cursor.execute('''
                SELECT * FROM SubExcelData 
                WHERE sub_table_id = ? AND username = ?
            ''', (sub_sequence, username))
            sub_data_rows = cursor.fetchall()
            for row in sub_data_rows:
                sub_data_dict = {description[0]: row[i] for i, description in enumerate(cursor.description)}
                sub_excel_data.append(sub_data_dict)

        # 组成最终返回的数据结构
        result = {
            "MainExcelTable": main_table_data,
            "SubExcelTable": sub_table_data,
            "SubExcelData": sub_excel_data
        }

        logging.info(f"成功获取数据，main_id: {main_id}, username: {username}")

        return result

    except sqlite3.Error as e:
        logging.error(f"数据库错误: {e}")
        return None
    except Exception as e:
        logging.error(f"发生未知错误: {e}")
        return None
    finally:
        # 确保数据库连接关闭
        if conn:
            conn.close()


# 通过username和id查询
def get_sub_table_data_from_sub_table_by_sub_id(id, username):
    """
    从 SubExcelTable 获取 sub_table_data 数据并解析为 JSON 格式。

    :param id: 子表 ID
    :param username: 用户名
    :return: 如果存在且格式正确则返回解析后的 JSON 数据，否则返回 None
    """
    conn = None
    cursor = None
    try:
        # 连接到 SQLite 数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询 sub_table_data 字段
        cursor.execute('''
            SELECT sub_table_data 
            FROM SubExcelTable 
            WHERE username = ? AND sequence = ?
        ''', (username, id))

        result = cursor.fetchone()

        # 关闭数据库连接
        cursor.close()
        conn.close()

        # 返回解析后的 JSON 数据
        if result and result[0]:
            try:
                # 将 sub_table_data 字符串转换为 JSON 格式
                return json.loads(result[0])
            except json.JSONDecodeError as e:
                logging.error(f"JSON 解析错误: {e}，输入数据: {result[0]}")
                return None
        else:
            return None  # 若无数据或已删除返回 None

    except sqlite3.Error as e:
        logging.error(f"数据库错误: {e}")
        return None
    except Exception as e:
        logging.error(f"发生未知错误: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_sequences_older_than_30_days(username):
    """
    获取超过30天的 sequence 列表，以及 type 在指定范围内且 event_time 超过30天的去重 main_table_id 列表。

    :param username: 用户名
    :return: 一个包含两个列表的字典：
             - "sequences": 超过30天的 sequence 列表
             - "main_table_ids": 去重后的 main_table_id 列表
    """
    # 获取波兰时区
    poland_tz = pytz.timezone('Europe/Warsaw')

    # 当前波兰时间，并计算出30天前的时间
    try:
        now_in_poland = datetime.now(poland_tz)
        thirty_days_ago = (now_in_poland - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logging.error(f"获取波兰时间失败: {e}")
        return {"main_table_ids": [], "xml_table_ids": []}

    conn = None
    cursor = None
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询 MainExcelTable 中超过 30 天的 sequence
        sequence_query = '''
            SELECT sequence 
            FROM MainExcelTable 
            WHERE username = ? 
            AND created_at < ?
        '''
        cursor.execute(sequence_query, (username, thirty_days_ago))
        sequences = [row[0] for row in cursor.fetchall()]

        # 查询 SubXMLData 中指定类型且 event_time 超过 30 天的去重 main_table_id
        types_to_query = ['upd', 'zc429', 'zcx03', 'zcx64', 'zcx65', 'zc410', 'zc460']
        main_table_id_query = '''
            SELECT DISTINCT main_table_id
            FROM SubXMLData
            WHERE username = ?
            AND type IN ({placeholders})
            AND event_time < ?
        '''.format(placeholders=','.join('?' for _ in types_to_query))

        params = [username] + types_to_query + [thirty_days_ago]
        cursor.execute(main_table_id_query, params)
        main_table_ids = list(set(row[0] for row in cursor.fetchall()))  # 去重

        return {"main_table_ids": sequences, "xml_table_ids": main_table_ids}

    except sqlite3.Error as e:
        logging.error(f"数据库错误: {e}")
        return {"main_table_ids": [], "xml_table_ids": []}
    except Exception as e:
        logging.error(f"发生未知错误: {e}")
        return {"main_table_ids": [], "xml_table_ids": []}
    finally:
        # 确保关闭数据库连接
        if conn:
            conn.close()


def delete_data_from_related_tables(list_time_out_ids):
    """
    删除相关表中的数据，包括：
    - SubXMLData 表中按 main_table_id 和 xml_list 删除相关数据。
    - SubExcelTable、SubExcelData、MainExcelTable 中按 main_table_id 删除相关数据。

    :param list_time_out_ids: 包含 main_table_ids 和 xml_table_ids 的字典
    :return: 是否成功删除（True/False）
    """
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sequence_list = []
    xml_list = []
    placeholders = ''

    try:
        # 启动事务
        conn.execute('BEGIN')
        sequence_list = list_time_out_ids['main_table_ids']
        xml_list = list_time_out_ids['xml_table_ids']

        # 1. 删除 SubXMLData 表中的数据（按 main_table_id），再删除SignatureForm表中对应的数据
        # 获取 SubXMLData 表中的 messageID, sub_table_id, type, direction
        if sequence_list:
            placeholders = ','.join('?' for _ in sequence_list)

            # 查询 SubXMLData 表获取相关数据
            cursor.execute(f'''
                SELECT messageID, sub_table_id, type, direction 
                FROM SubXMLData 
                WHERE main_table_id IN ({placeholders})
            ''', tuple(sequence_list))

            rows = cursor.fetchall()  # 获取查询结果

            # 如果有数据需要删除 SignatureForm
            if rows:
                # 解析查询结果
                delete_values = [(row[0], row[1], row[2], row[3]) for row in rows]

                # 构造删除 SignatureForm 的 SQL 语句
                cursor.executemany('''
                    DELETE FROM SignatureForm 
                    WHERE main_id = ? AND related_id = ? AND type = ? AND direction = ?
                ''', delete_values)

            # 删除 SubXMLData 表中数据
            cursor.execute(f'''
                DELETE FROM SubXMLData 
                WHERE main_table_id IN ({placeholders})
            ''', tuple(sequence_list))

        # 2. 获取所有与 sequence_list 中的 MainExcelTable 相关的 sub_table_id
        if sequence_list:
            cursor.execute(f'''
                SELECT sequence FROM SubExcelTable 
                WHERE main_id IN ({placeholders})
            ''', tuple(sequence_list))

            # 获取所有的 sub_table_id
            sub_table_ids = [row[0] for row in cursor.fetchall()]

            # 如果有相关的 sub_table_id，删除 SubExcelData 中的记录
            if sub_table_ids:
                sub_placeholders = ','.join('?' for _ in sub_table_ids)
                cursor.execute(f'''
                    DELETE FROM SubExcelData 
                    WHERE sub_table_id IN ({sub_placeholders})
                ''', tuple(sub_table_ids))

            # 3. 删除 SubExcelTable 表中的数据（按 main_id）
            cursor.execute(f'''
                DELETE FROM SubExcelTable 
                WHERE main_id IN ({placeholders})
            ''', tuple(sequence_list))

        # 4. 删除 MainExcelTable 表中的数据（按 sequence）
        if sequence_list:
            cursor.execute(f'''
                DELETE FROM MainExcelTable 
                WHERE sequence IN ({placeholders})
            ''', tuple(sequence_list))

        message_entries = []
        # 5. 先获取要删除的 messageID, sub_table_id, type, direction
        if xml_list:
            xml_placeholders = ','.join('?' for _ in xml_list)
            cursor.execute(f'''
                SELECT messageID, sub_table_id, type, direction FROM SubXMLData 
                WHERE main_table_id IN ({xml_placeholders})
            ''', tuple(xml_list))

            # 获取所有符合条件的记录
            message_entries = cursor.fetchall()

            # 先删除 SubXMLData 表中的数据
            cursor.execute(f'''
                DELETE FROM SubXMLData 
                WHERE main_table_id IN ({xml_placeholders})
            ''', tuple(xml_list))

        # 6. 再删除 SignatureForm 表中的数据（按 messageID, sub_table_id, type, direction）
        if message_entries:
            delete_conditions = ' OR '.join(
                '(main_id = ? AND related_id = ? AND type = ? AND direction = ?)' for _ in message_entries)
            delete_values = [value for row in message_entries for value in row]  # 将元组列表展平为单个列表

            cursor.execute(f'''
                DELETE FROM SignatureForm 
                WHERE {delete_conditions}
            ''', tuple(delete_values))

        # 提交事务
        conn.commit()

        # 记录成功日志
        logging.info(f"Successfully deleted records for sequences: {sequence_list} and xml_list: {xml_list}")
        return True

    except Exception as e:
        # 如果发生错误，回滚事务并返回 False
        conn.rollback()
        logging.error(f"Error deleting records for sequences {sequence_list} or xml_list {xml_list}: {e}")
        return False

    finally:
        # 关闭连接
        conn.close()


# 查询subtable里的state是什么
def is_state_sent_of_sub_table(sequence, username):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 查询state字段是否为'Sent'
        cursor.execute('''
            SELECT state FROM SubExcelTable
            WHERE sequence = ? AND username = ? AND deleted_at IS NULL
        ''', (sequence, username))

        result = cursor.fetchone()

        if result and result[0] == "Sent":
            return True

        return False  # 如果没有结果或者状态不是 "Sent"

    except Exception as e:
        # 记录错误日志
        logging.error(f"Error querying state for sequence {sequence} and username {username}: {e}")
        return False

    finally:
        cursor.close()
        conn.close()


# 获取4个数据表中所有的数据
def fetch_all_data():
    conn = None
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询 MainExcelTable 表中的所有数据
        cursor.execute("SELECT * FROM MainExcelTable WHERE deleted_at IS NULL")
        main_excel_data = cursor.fetchall()

        # 查询 SubExcelTable 表中的所有数据
        cursor.execute("SELECT * FROM SubExcelTable WHERE deleted_at IS NULL")
        sub_excel_data = cursor.fetchall()

        # 查询 SubExcelData 表中的所有数据
        cursor.execute("SELECT * FROM SubExcelData WHERE deleted_at IS NULL")
        sub_excel_data_list = cursor.fetchall()

        # 查询 SubXMLData 表中的所有数据
        cursor.execute("SELECT * FROM SubXMLData WHERE deleted_at IS NULL")
        sub_xml_data = cursor.fetchall()

        # 返回包含 4 个列表的元组
        return main_excel_data, sub_excel_data, sub_excel_data_list, sub_xml_data

    except sqlite3.OperationalError as e:
        print(f"数据库操作错误: {e}")
        return [], [], [], []

    except sqlite3.DatabaseError as e:
        print(f"数据库连接错误: {e}")
        return [], [], [], []

    except Exception as e:
        print(f"发生未知异常: {e}")
        return [], [], [], []

    finally:
        # 确保数据库连接被关闭
        if conn:
            conn.close()


def get_main_table_data_by_sequence(sequence):
    conn = None
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询数据
        query = '''
        SELECT main_table_data 
        FROM MainExcelTable 
        WHERE sequence = ? AND deleted_at IS NULL
        '''
        cursor.execute(query, (sequence,))
        result = cursor.fetchone()

        if result:
            main_table_data = result[0]  # 获取查询结果
            # 尝试将 main_table_data 转为 JSON 格式
            try:
                main_table_json = json.loads(main_table_data)
            except json.JSONDecodeError:
                raise ValueError("main_table_data 不是有效的 JSON 格式")
            return main_table_json
        else:
            raise ValueError(f"未找到 sequence 为 {sequence} 的记录或记录已被软删除")
    except sqlite3.Error as e:
        # 捕获数据库操作异常
        raise RuntimeError(f"数据库操作失败: {e}")
    finally:
        # 确保关闭数据库连接
        if conn:
            conn.close()


def get_airwaybill_ioss_trackingnumber(sub_sequence):
    """
    根据 SubExcelTable 的 sequence 查询 AirWayBill、IOSS 和 TrackingNumber。

    参数:
        sub_sequence (str): SubExcelTable 的唯一序列号。

    返回:
        tuple: (AirWayBill, IOSS, TrackingNumber)，如果查询失败返回 None。
    """
    conn = None
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询 SubExcelTable 获取 main_id, IOSS 和 TrackingNumber
        sub_query = """
        SELECT main_id, IOSS, TrackingNumber 
        FROM SubExcelTable 
        WHERE sequence = ? AND deleted_at IS NULL
        """
        cursor.execute(sub_query, (sub_sequence,))
        sub_result = cursor.fetchone()

        # 如果未查到数据，直接返回 None
        if not sub_result:
            print(f"SubExcelTable 中未找到 sequence 为 {sub_sequence} 的记录。")
            return None

        main_id, ioss, tracking_number = sub_result

        # 使用 main_id 查询 MainExcelTable 获取 AirWayBill
        main_query = """
        SELECT AirWayBill 
        FROM MainExcelTable 
        WHERE sequence = ? AND deleted_at IS NULL
        """
        cursor.execute(main_query, (main_id,))
        main_result = cursor.fetchone()

        # 如果未查到数据，直接返回 None
        if not main_result:
            print(f"MainExcelTable 中未找到 sequence 为 {main_id} 的记录。")
            return None

        air_way_bill = main_result[0]

        # 返回查询结果
        return air_way_bill, ioss, tracking_number, main_id

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_sub_table_data_by_id(sub_table_id):
    """
    根据 sub_table_id 查询 SubXMLData 表中的数据，返回指定格式的字典列表，并将 json_data 转换为 JSON 格式。
    :param sub_table_id: 子表的 ID，用于查询数据。如果为 None，则查询 sub_table_id IS NULL 的记录。
    :return: 包含查询结果的字典列表
    """
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        # 动态构造 SQL 查询条件
        if sub_table_id is None:
            query = '''
                SELECT sub_table_id, main_table_id, type, event_time, xml_json_data, direction, CR, messageID
                FROM SubXMLData
                WHERE sub_table_id IS NULL AND deleted_at IS NULL
            '''
            cursor.execute(query)
        else:
            query = '''
                SELECT sub_table_id, main_table_id, type, event_time, xml_json_data, direction, CR, messageID
                FROM SubXMLData
                WHERE sub_table_id = ? AND deleted_at IS NULL
            '''
            cursor.execute(query, (sub_table_id,))

        # 获取查询结果
        rows = cursor.fetchall()

        # 构造结果列表
        result = []
        for row in rows:
            try:
                # 尝试将 json_data 转换为 JSON 对象
                json_data = json.loads(row[4]) if row[4] else None
            except json.JSONDecodeError:
                # 如果转换失败，记录错误并存储原始数据
                print(f"JSON 解析错误: {row[4]}")
                json_data = row[4]

            result.append({
                "sub_id": row[0],
                "main_id": row[1],
                "type": row[2],
                "event_time": row[3],
                "json_data": json_data,  # 存储转换后的 JSON 对象或原始数据
                "direction": row[5],
                "CR": row[6],
                'messageID': row[7],
            })

        return result
    except Exception as e:
        print(f"查询时发生错误: {e}")
        return []
    finally:
        conn.close()


def get_account_data(username=None, data_types=None, event_time=None):
    """
    获取符合条件的 XML 数据，每个 main_table_id 保留一条记录，按 type 和 event_time DESC 排序。

    参数:
        username (str): 用户名，用于过滤数据。
        data_types (list[str]): 数据类型列表，支持多个类型进行查询。
        event_time (str): 事件时间，格式 'YYYY-MM-DD HH:MM:SS'，只挑选 event_time >= 这个时间的数据。

    返回:
        list[tuple]: 查询到的 XML 数据，按 type 和 event_time DESC 排序。
    """
    if not data_types or not isinstance(data_types, list):
        raise ValueError("参数 data_types 必须是一个非空的列表")
    if not username:
        raise ValueError("参数 username 不能为空")

    conn = None
    results = []

    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 构建查询语句
        placeholders = ', '.join(['?'] * len(data_types))  # 为 IN 子句构建占位符
        query = f"""
            SELECT *
            FROM SubXMLData
            WHERE type IN ({placeholders})
              AND deleted_at IS NULL
              AND username = ?
        """

        # 构建参数列表
        params = data_types + [username]

        # 如果 event_time 不为空，添加筛选条件
        if event_time:
            query += " AND event_time >= ?"
            params.append(event_time)

        query += " ORDER BY type, event_time DESC"

        # 执行查询
        cursor.execute(query, params)
        results = cursor.fetchall()

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，用户名: {username}，数据类型: {data_types}，时间: {event_time}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，用户名: {username}，数据类型: {data_types}，时间: {event_time}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

    return results


def get_cr_xml_data_by_main_id(main_id, username=None):
    """
    根据 main_table_id 查找所有 CR 为 '1' 的数据，按 type 排序，再按 event_time 升序排序。

    :param main_id: 主表 ID
    :param username: 用户名（可选）
    :return: 查询结果列表
    """
    conn = None
    xml_data = []
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询符合条件的数据
        if username:
            cursor.execute("""
                SELECT * FROM SubXMLData 
                WHERE main_table_id = ? AND deleted_at IS NULL AND username = ? AND CR = '1'
                ORDER BY type, event_time ASC
            """, (main_id, username))
        else:
            cursor.execute("""
                SELECT * FROM SubXMLData 
                WHERE main_table_id = ? AND deleted_at IS NULL AND CR = '1'
                ORDER BY type, event_time ASC
            """, (main_id,))

        # 获取查询结果
        xml_data = cursor.fetchall()
        print(f"成功获取 main_table_id 为 {main_id} 的 CR='1' 的 XML 数据。")

    except sqlite3.DatabaseError as e:
        logging.error(f"数据库错误: {e}，main_table_id: {main_id}，用户名: {username}")
        print(f"数据库错误: {e}")
    except Exception as e:
        logging.error(f"未知错误: {e}，main_table_id: {main_id}，用户名: {username}")
        print(f"未知错误: {e}")
    finally:
        # 关闭数据库连接
        if conn:
            conn.close()

    # 返回查询到的 XML 数据
    return xml_data


def get_receive_upd(username, flag=0):
    """
    查找满足条件的记录，并按 event_time 降序排序：
    1. type 为 'upd'；
    2. direction 为 'receive'；
    3. main_table_id 是唯一的，且没有对应的 direction 为 'send' 的记录；
    4. username 符合指定的值。

    参数：
        username: 要过滤的用户名。

    返回：
        List[Tuple]: 满足条件的记录列表，每条记录包含完整行数据。
    """
    conn = None
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if flag == 1:
            # 查询逻辑，按 event_time 降序排序
            query = """
                SELECT *
                FROM SubXMLData r
                WHERE r.type = 'upd'
                  AND r.direction = 'receive'
                  AND r.username = ?
                  AND NOT EXISTS (
                      SELECT 1
                      FROM SubXMLData s
                      WHERE s.main_table_id = r.main_table_id
                        AND s.direction = 'send'
                  )
                ORDER BY r.event_time DESC
                """
        elif flag == 0:
            query = """
            SELECT *
            FROM SubXMLData r
            WHERE r.type = 'upd'
              AND r.direction = 'receive'
              AND r.username = ?
            ORDER BY r.event_time DESC
            """
        cursor.execute(query, (username,))
        result = cursor.fetchall()

        return result

    except sqlite3.Error as e:
        print(f"数据库操作失败: {e}")
        return []
    finally:
        # 确保连接关闭
        if conn:
            conn.close()


def get_send_upd(username):
    """
    查找满足以下条件的记录：
    1. type 为 'upd'；
    2. direction 为 'send'；
    3. username 匹配指定的值。

    参数：
        username (str): 要过滤的用户名。

    返回：
        List[Tuple]: 满足条件的记录列表，每条记录包含完整行数据。
    """
    conn = None
    results = []
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查询 type 为 upd 且 direction 为 send 的数据
        cursor.execute('''
                SELECT * FROM SubXMLData
                WHERE type = ? AND direction = ? AND username = ?
                ORDER BY event_time DESC
            ''', ('upd', 'send', username))

        # 获取查询结果
        results = cursor.fetchall()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Exception in get_sent_upd: {e}")
    finally:
        if conn:
            conn.close()

    return results


def get_upd_by_id(username, record_ids):
    """
    根据用户名和多个 ID，从 SubXMLData 表中查找数据，并返回包含指定字段的字典列表。

    参数:
        username (str): 用户名，用于过滤数据。
        record_ids (list): 要查找的记录 ID 列表。

    返回:
        List[dict]: 满足条件的记录列表，每条记录是一个包含 main_id、xml_data 和 event_time 的字典。
    """
    if not record_ids:
        print("record_ids 列表为空，无法查询数据。")
        return []

    conn = None
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 构造查询语句，将 record_ids 转换为占位符
        placeholders = ",".join("?" for _ in record_ids)
        query = f"""
                SELECT main_table_id, xml_json_data, event_time, messageID, sub_table_id, direction, username 
                FROM SubXMLData
                WHERE username = ? AND id IN ({placeholders});
                """
        # 执行查询
        cursor.execute(query, (username, *record_ids))
        rows = cursor.fetchall()

        # 将结果转换为字典列表
        result = [
            {
                "main_id": row[0],
                "xml_data": row[1],
                "event_time": row[2],
                'messageID': row[3],
                'sub_id': row[4],
                'direction': row[5],
                'username': row[6]
            }
            for row in rows
        ]

        return result

    except Exception as e:
        print(f"查询数据时发生错误: {e}")
        return []

    finally:
        if conn:
            conn.close()


def get_cr_air_way_bill(username, sequence):
    """
    根据用户名和序列号，从 MainExcelTable 表中查找 AirWayBill。

    参数:
        username (str): 用户名，用于过滤数据。
        sequence (str): 序列号，用于查找对应的记录。

    返回:
        str: 如果找到记录，返回对应的 AirWayBill；否则返回 None。
    """
    conn = None
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 构造查询语句
        query = """
        SELECT AirWayBill
        FROM MainExcelTable
        WHERE username = ? AND sequence = ?;
        """
        # 执行查询
        cursor.execute(query, (username, sequence))
        result = cursor.fetchone()

        # 返回查询结果
        if result:
            return result[0]  # AirWayBill
        else:
            return None

    except Exception as e:
        print(f"查询数据时发生错误: {e}")
        return None

    finally:
        if conn:
            conn.close()


def get_cr_xml_json_data(username, main_table_id, type):
    """
    根据用户名、main_table_id 和 type 查找对应的 xml_json_data 和 event_time。

    参数:
        username (str): 用户名，用于过滤数据。
        main_table_id (str): 主表的 ID，用于查找对应的记录。
        type (str): 类型字段，用于过滤数据。

    返回:
        list[dict]: 如果找到记录，返回包含 xml_json_data 和 event_time 的字典列表；否则返回空列表。
    """
    conn = None
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 构造查询语句
        query = """
                SELECT xml_json_data, event_time, messageID, sub_table_id, direction, username
                FROM SubXMLData
                WHERE username = ? AND main_table_id = ? AND type = ?;
                """
        # 执行查询
        cursor.execute(query, (username, main_table_id, type))
        results = cursor.fetchall()

        # 返回查询结果
        return [
            {
                'xml_json_data': row[0],
                'event_time': row[1],
                'messageID': row[2],
                'sub_id': row[3],
                'direction': row[4],
                'username': row[5]
            }
            for row in results
        ]

    except Exception as e:
        print(f"查询数据时发生错误: {e}")
        return []

    finally:
        if conn:
            conn.close()


def get_xml_data_by_type(username, data_types):
    """
    根据用户名和数据类型查找所有符合条件的数据，并按 event_time 降序排序。

    参数:
        username (str): 用户名，用于过滤数据。
        data_types (list): 数据类型列表，指定需要查找的类型。

    返回:
        list: 包含查询结果的列表，每个元素为一个字典。
    """
    conn = None
    results = []

    try:
        # 检查参数有效性
        if not isinstance(data_types, list) or not data_types:
            raise ValueError("data_types 必须是一个非空列表")

        # 连接到数据库
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 启用字典游标
        cursor = conn.cursor()

        # 构建查询语句
        placeholders = ",".join("?" for _ in data_types)  # 为类型列表构造占位符
        query = f"""
        SELECT * 
        FROM SubXMLData 
        WHERE username = ? 
          AND type IN ({placeholders}) 
          AND deleted_at IS NULL
        ORDER BY event_time DESC
        """

        # 执行查询
        cursor.execute(query, [username, *data_types])
        results = cursor.fetchall()

    except sqlite3.DatabaseError as e:
        print(f"数据库错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
    finally:
        if conn:
            conn.close()

    return results


def synchronize_signature_form(signature_datas):
    """
    将 signature_datas 中的所有数据插入到 SignatureForm 表中。
    在插入之前会检查是否已存在相同的 main_id、data、direction 和 username，避免重复插入。

    :param signature_datas: 包含多个字典的列表，每个字典有:
        - "main_id": str
        - "data": dict  (JSON 格式存储)
        - "direction": str
        - "username": str
    """
    conn = None
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for item in signature_datas:
            message_id = item.get("main_id")
            data_dict = item.get("data", {})  # data 是一个字典
            direction = item.get("direction")
            related_id = item.get("related_id")
            type_value = item.get("type")
            username = item.get("username")

            if not message_id or not username or direction is None:
                continue  # 跳过无效数据

            # 将 data_dict 转换为 JSON 字符串
            data_json = json.dumps(data_dict, ensure_ascii=False)

            # 检查数据库是否已存在相同记录
            cursor.execute('''
                SELECT COUNT(*)
                FROM SignatureForm
                WHERE main_id = ? AND data = ? AND username = ? AND direction = ? AND related_id = ? AND type = ?
            ''', (message_id, data_json, username, direction, related_id, type_value))
            count = cursor.fetchone()[0]

            # 如果数据不存在，则插入
            if count == 0:
                cursor.execute('''
                    INSERT INTO SignatureForm (main_id, data, username, direction, related_id, type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (message_id, data_json, username, direction, related_id, type_value))

        # 提交事务
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()


def get_signature_info_by_message_id_direction_and_username(message_id, direction, username, related_id, type_value):
    """
    根据 main_id 和 username 查找 data 信息。

    :param message_id: 要查询的 messageID
    :param direction: 要查询的 direction
    :param username: 要查询的 username
    :param type_value:
    :param related_id:
    :return: JSON 格式的字符串，如果未找到则返回 None
    """
    conn = None
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if related_id is None:
            query = '''
                    SELECT data 
                    FROM SignatureForm 
                    WHERE main_id = ? 
                        AND username = ? 
                        AND direction = ?
                        AND related_id IS NULL 
                        AND type = ?
                '''
            params = (message_id, username, direction, type_value)
        else:
            query = '''
                    SELECT data 
                    FROM SignatureForm 
                    WHERE main_id = ? 
                        AND username = ? 
                        AND direction = ? 
                        AND related_id = ? 
                        AND type = ?
                '''
            params = (message_id, username, direction, related_id, type_value)

        cursor.execute(query, params)
        # 获取结果
        result = cursor.fetchone()

        # 直接返回 data（JSON 字符串）或 None
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()
