import inspect
import sqlite3

class Database:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)

    @property
    def tables(self):
        SELECT_TABLES = "SELECT name FROM sqlite_master WHERE type='table';"
        return [row[0] for row in self.conn.execute(SELECT_TABLES).fetchall()]
        

    def create(self, table):
        self.conn.execute(table._get_create_sql())


    def save(self, instance):
        sql, values = instance._get_insert_sql()
        cursor = self.conn.execute(sql, values)
        self.conn.commit()
        instance.data["id"] = cursor.lastrowid


    def all(self, table):
        sql, fields = table._get_select_all_sql()
        result = []
        for row in self.conn.execute(sql).fetchall():
            instance = table()
            for fields, value in zip(fields, row):
                if fields.endswith("_id"):
                    fields = fields[:-3]
                    fk = getattr(table, fields)
                    value = self.get(fk.table, id=value)
                setattr(instance, fields, value)
            result.append(instance)
        return result
    
    def get(self, table, id):
        sql, fields = table._get_select_by_id_sql(id)
        row = self.conn.execute(sql).fetchone()

        if row is None:
            raise Exception(f"{table.__name__} instance with id {id} does not exist")

        instance = table()
        for fields, value in zip(fields, row):
            if fields.endswith("_id"):
                fields = fields[:-3]
                fk = getattr(table, fields)
                value = self.get(fk.table, id=value)
            setattr(instance, fields, value)
        return instance
    

    def update(self, instance):
        sql, values = instance._get_update_sql()
        self.conn.execute(sql, values)
        self.conn.commit()


    def delete(self, table, id):
        sql = table._get_delete_sql(id)
        self.conn.execute(sql)
        self.conn.commit()    




class Table:
    def __init__(self, **kwargs):
        self._data = {
            "id": None
        }

        for key, value in kwargs.items():
            self._data[key] = value
    @classmethod
    def _get_create_sql(cls):
        CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {name} ({fields});"
        fields = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT",
        ]

        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(f"{name} {col.sql_type}")
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id INTEGER")
        
        fields = ", ".join(fields)
        name = cls.__name__.lower()
        return CREATE_TABLE.format(name=name, fields=fields)
    
    def __getattribute__(self, attr_name):
        _data = super().__getattribute__("_data")
        if attr_name in _data:
            return _data[attr_name]
        
        return super().__getattribute__(attr_name)
    

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name in self._data:
            self._data[name] = value
         
    
    def _get_insert_sql(self):
        INSERT_SQL = "INSERT INTO {name} ({fields}) VALUES ({placeholders});"
        cls = self.__class__
        fields = []
        placeholders = []
        values = []

        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(name)
                values.append(getattr(self, name))
                placeholders.append("?")
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id")
                values.append(getattr(self, name).id)
                placeholders.append("?")

        fields = ", ".join(fields)
        placeholders = ", ".join(placeholders)

        sql = INSERT_SQL.format(
            name=cls.__name__.lower(),
            fields=fields,
            placeholders=placeholders,
        )

        return sql, values 

    @classmethod
    def _get_select_all_sql(cls):
        SELECT_ALL_SQL = "SELECT {fields} FROM {name};"

        filter = ["id"]
        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                filter.append(name)
            elif isinstance(col, ForeignKey):
                filter.append(f"{name}_id")

        sql = SELECT_ALL_SQL.format(
            name=cls.__name__.lower(),
            fields=", ".join(filter)
        )

        return sql, filter
    
    @classmethod
    def _get_select_by_id_sql(cls, id):
        SELECT_BY_ID_SQL = "SELECT {fields} FROM {name} WHERE id = {id};"

        fields = ["id"]
        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(name)
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id")

        sql = SELECT_BY_ID_SQL.format(
            name=cls.__name__.lower(),
            id=id,
            fields=", ".join(fields)
        )

        return sql, fields
    

    def _get_update_sql(self):
        UPDATE_SQL = "UPDATE {name} SET {fields} WHERE id = {id};"
        fields = []
        values = []

        for name, col in inspect.getmembers(self.__class__):
            if isinstance(col, Column):
                fields.append(f"{name} = ?")
                values.append(getattr(self, name))
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id = ?")
                values.append(getattr(self, name).id)

        sql = UPDATE_SQL.format(
            name=self.__class__.__name__.lower(),
            fields=", ".join([f"{fields} = ?" for fields in fields]),
            id=self.id
        )

        return sql, values
    
    @classmethod
    def _get_delete_sql(cls, id):
        DELETE_SQL = "DELETE FROM {name} WHERE id = {id};"
        sql = DELETE_SQL.format(
            name=cls.__name__.lower(),
            id=id
            
        )
        return sql

class Column:
    def __init__(self, column_type):
        self.type = column_type

    @property
    def sql_type(self):
        SQLITE_TYPE_MAP = {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            bytes: "BLOB",
            bool: "INTEGER",
            
        }
        return SQLITE_TYPE_MAP[self.type]  


class ForeignKey:
    def __init__(self, table):
        self.table = table
