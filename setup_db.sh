sqlite3 bot.db "create table ranking (id integer primary key, lowername text, name text, score integer)"
sqlite3 bot.db "create table links (url text primary key, name text)"
sqlite3 bot.db "create table admins (id integer primary key, lowername text, name text)"
