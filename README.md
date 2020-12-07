# KissDB
## Keep It Simple, Stupid - Database Server
---
### About
KissDB is a very simple key-value NoSQL database server built for small- to medium-scale data storage needs. It includes multithreading, file locking, and a RESTful API. It has a theoretically infiite table and field size depending on available disk space, mitigating one of the main hassles of SQL databases. Its main intended purpose is JSON storage, but any textual data can be stored.
### Security
The server will eventually implement authentication, but for the moment should be hidden behind localhost with a firewall in place blocking outside access to its bound port. Once authentication is implemented, it should still be hidden behind localhost and proxied via HTTPS using nginx or a similar server.