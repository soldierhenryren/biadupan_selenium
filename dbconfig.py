from peewee import Model, OperationalError, MySQLDatabase, __exception_wrapper__

class RetryOperationalError(object):

    def execute_sql(self, sql, params=None, commit=True):
        try:
            cursor = super(RetryOperationalError, self).execute_sql(
                sql, params, commit)
        except OperationalError:
            if not self.is_closed():
                self.close()
            with __exception_wrapper__:
                cursor = self.cursor()
                cursor.execute(sql, params or ())
                if commit and not self.in_transaction():
                    self.commit()
        return cursor


class MyRetryDB(RetryOperationalError, MySQLDatabase):
    pass
db = MySQLDatabase('db_main',
                   host='120.27.71.187',
                   user='ssnn',
                   password='fin%QZQG?1-5')

# Model 类需要有一个类属性，其database 属性是一个 连接对象
class BaseModel(Model):
    class Meta:
        database = db
    @staticmethod
    def query_view(view_name):
        for viewdata in db.get_views():
            if viewdata.name == view_name:
                cursor = db.execute_sql(viewdata.sql)
                for (id,word, frequency) in cursor:
                    print(str(id),':',word, '->', str(frequency))

