import os
import pytest
from pyframe.app import PyWebHiveApp
import pytest
from pyframe.orm import Database, Table, Column, ForeignKey

@pytest.fixture
def app():
    return PyWebHiveApp()

@pytest.fixture
def test_client(app):
    return app.test_session()


@pytest.fixture
def Author():
    class Author(Table):
        name = Column(str)
        age = Column(int)
    return Author

@pytest.fixture
def Book(Author):
    class Book(Table):
        title = Column(str)
        published = Column(bool)
        author = Column(Author)
    return Book

@pytest.fixture
def db():
    if os.path.exists("./test.db"):
        os.remove("./test.db")
    db = Database("./test.db")
    return db
