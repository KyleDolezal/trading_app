from pg_adapter import PG_Adapter

class MockPG(object):
    def cursor(args):
        return MockCursor()

class MockCursor(object):
    def execute(self, arg):
        assert arg == "select * from table;"

    def fetchall(arg):
        pass

def test_exec_query(mocker):
    mocked_pg_con = mocker.patch('pg_adapter.psycopg2.connect', return_value=MockPG())
    pg_adapter = PG_Adapter()

    pg_adapter.exec_query("select * from table;")
