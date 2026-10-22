import sqlite3,tempfile,unittest
from pathlib import Path
from sqlite_playground import connect,add,update,remove,seed
class DatabaseTests(unittest.TestCase):
    def setUp(self): self.db=connect(':memory:')
    def tearDown(self): self.db.close()
    def test_crud_and_injection(self):
        title="'); DROP TABLE tasks;--";i=add(self.db,title)
        self.assertEqual(self.db.execute('SELECT title FROM tasks').fetchone()[0],title)
        update(self.db,i,done=True);self.assertEqual(self.db.execute('SELECT done FROM tasks').fetchone()[0],1)
        remove(self.db,i);self.assertEqual(self.db.execute('SELECT count(*) FROM tasks').fetchone()[0],0)
    def test_rollback(self):
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db:
                self.db.execute("INSERT INTO tasks(title) VALUES ('valid')")
                self.db.execute("INSERT INTO tasks(title) VALUES ('')")
        self.assertEqual(self.db.execute('SELECT count(*) FROM tasks').fetchone()[0],0)
    def test_seed(self): seed(self.db);self.assertEqual(self.db.execute('SELECT count(*) FROM tasks').fetchone()[0],3)
    def test_upgrade(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'old.db';db=sqlite3.connect(p)
            db.execute('CREATE TABLE tasks(id INTEGER PRIMARY KEY,title TEXT,done INTEGER DEFAULT 0)');db.execute('PRAGMA user_version=1');db.commit();db.close()
            db=connect(p);self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],2)
            self.assertTrue(db.execute("SELECT name FROM sqlite_master WHERE name='tasks_done_idx'").fetchone());db.close()
    def test_missing(self):
        with self.assertRaises(ValueError): remove(self.db,42)
