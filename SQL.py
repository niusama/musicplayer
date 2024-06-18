import pymysql
import UI

host = 'localhost'
user = 'root'
password = '1735585597'
db = 'py_exp'

def connect(sql):
    #连接数据库
    try:
        conn = pymysql.connect(host=host, user=user, password=password, db=db)
        cur = conn.cursor()
    except:
        UI.pop_prompt('温馨提示', '数据库连接错误')
        exit(1)

    #执行sql语句
    try:
        cur.execute(sql)
        conn.commit()
    except:
        conn.rollback()
        cur.close()
        conn.close()
        return None, None
    return conn, cur


