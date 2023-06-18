# What is this?

This is part of a distributed system. To understand the project as a whole look at [this repo](https://github.com/Ziad-Nasr/Multiplayer-2DCarRacing).

# How to run?

You will need to install

1. flask
2. flask_mysqldb

To run type 

```bash
$ python db_connection.py
```

To run this on a server in order to keep it running after terminating ssh session type:

```bash
$ disown $(python db_connection.py) &
```
