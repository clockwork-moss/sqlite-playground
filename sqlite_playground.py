"""A small SQLite task notebook with versioned migrations."""
import argparse,json,sqlite3
MIGRATIONS=["CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL CHECK(length(trim(title))>0), done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0,1)))", "CREATE INDEX tasks_done_idx ON tasks(done)"]
def connect(path):
    db=sqlite3.connect(path);db.row_factory=sqlite3.Row
    try:
        db.execute('BEGIN IMMEDIATE')
        version=db.execute('PRAGMA user_version').fetchone()[0]
        if version>len(MIGRATIONS): raise ValueError('database schema is newer than this application')
        for i in range(version,len(MIGRATIONS)):
            db.execute(MIGRATIONS[i]);db.execute(f'PRAGMA user_version={i+1}')
        db.commit();return db
    except Exception:
        db.rollback();db.close();raise

def add(db,title):
    if not title.strip(): raise ValueError('title must not be empty')
    with db: return db.execute('INSERT INTO tasks(title) VALUES (?)',(title,)).lastrowid

def update(db,ident,title=None,done=None):
    with db:
        row=db.execute('SELECT * FROM tasks WHERE id=?',(ident,)).fetchone()
        if row is None: raise ValueError('task not found')
        title=row['title'] if title is None else title
        if not title.strip(): raise ValueError('title must not be empty')
        db.execute('UPDATE tasks SET title=?, done=? WHERE id=?',(title,row['done'] if done is None else int(done),ident))
def remove(db,ident):
    with db:
        if not db.execute('DELETE FROM tasks WHERE id=?',(ident,)).rowcount: raise ValueError('task not found')
def seed(db):
    with db:
        db.executemany('INSERT INTO tasks(title) VALUES (?)', [('Try a parameterized query',),('Inspect the status index',),('Make a backup',)])
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',default='tasks.db');s=p.add_subparsers(dest='command',required=True)
    s.add_parser('init');s.add_parser('seed');q=s.add_parser('list');q.add_argument('--done',choices=['yes','no'])
    q=s.add_parser('add');q.add_argument('title')
    q=s.add_parser('update');q.add_argument('id',type=int);q.add_argument('--title');q.add_argument('--done',choices=['yes','no'])
    q=s.add_parser('delete');q.add_argument('id',type=int);a=p.parse_args();db=None
    try:
        db=connect(a.db)
        if a.command=='add': print(add(db,a.title))
        elif a.command=='update': update(db,a.id,a.title,None if a.done is None else a.done=='yes')
        elif a.command=='delete': remove(db,a.id)
        elif a.command=='seed': seed(db)
        elif a.command=='list':
            rows=db.execute('SELECT * FROM tasks ORDER BY id') if a.done is None else db.execute('SELECT * FROM tasks WHERE done=? ORDER BY id',(int(a.done=='yes'),))
            print(json.dumps([dict(r) for r in rows]))
        else: print('Database initialized at schema version 2')
    except (ValueError,sqlite3.Error) as e: p.error(str(e))
    finally:
        if db is not None: db.close()
if __name__=='__main__': main()
