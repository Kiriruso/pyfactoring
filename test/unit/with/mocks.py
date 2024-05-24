# ruff: noqa

with open(r"test\filepath.py", "r", encoding="utf-8") as file:
    source = file.read()

with open('__const_0__', '__const_1__', encoding='__const_2__') as __var_0__:
    __local_0__ = __var_0__.read()

# ================================ #

async with session() as session:
    async with session.connect() as conn:
        data = await conn.execute("SQL QUERY")

async with session() as __var_0__:
    async with __var_0__.connect() as __local_0__:
        __local_1__ = await __local_0__.execute('__const_0__')
