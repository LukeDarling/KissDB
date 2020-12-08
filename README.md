# KissDB
## Keep It Simple, Stupid - Database Server
### About
KissDB is a very simple key-value NoSQL database server built for small- to medium-scale data storage needs. It includes multithreading, file locking, and a RESTful API. It has a theoretically infiite table and box size depending on available disk space, mitigating one of the main hassles of SQL databases. Its main intended purpose is JSON storage, but any textual data can be stored.
### Security
The server will eventually implement authentication, but for the moment should be hidden behind localhost with a firewall in place blocking outside access to its bound port. Once authentication is implemented, it should still be hidden behind localhost and proxied via HTTPS using nginx or a similar server.
### API
```
<Required>
[Optional]
```
---
#### Create a database
##### Header
`POST /<database>`
##### Body
N/A

---
#### Create a table
##### Header
`POST /<database>/<table>`
##### Body
N/A

---
#### Create a box and optionally initialize its content
##### Header
`POST /<database>/<table>/<box>`
##### Body
`[content]`

---
#### Get a list of all databases on the server
##### Header
`GET /`
##### Body
N/A

---
#### Get a list of all tables in a given database
##### Header
`GET /<database>`
##### Body
N/A

---
#### Get a list of all boxes in a given database's table
##### Header
`GET /<database>/<table>`
##### Body
N/A

---
#### Get the contents of a given box
##### Header
`GET /<database>/<table>/<box>`
##### Body
N/A

---
#### Update the contents of a given box
##### Header
`PUT /<database>/<table>/<box>`
##### Body
`<content>`

---
#### Delete a given database
##### Header
`DELETE /<database>`
##### Body
N/A

---
#### Delete a given database's table
##### Header
`DELETE /<database>/<table>`
##### Body
N/A

---
#### Delete a given database's given child table
##### Header
`DELETE /<database>/<table>`
##### Body
N/A

---
#### Delete a given database's given child table's box
##### Header
`DELETE /<database>/<table>/<box>`
##### Body
N/A
