drop table if exists users;
create table users(
  id integer primary key autoincrement,
  name string not null,
  pwd string not null,
  email string not null,
  age integer not null,
  birthday DATA not null,
  face string
);