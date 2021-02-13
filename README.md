# KissDB


## Keep It Simple, Stupid: Database Daemon


### About
KissDB is a very simple key-value NoSQL database daemon built for small- to medium-scale data storage needs. It offers simultaneous connections, resource locking, and a RESTful API. It has a theoretically infinite database, table, and box size depending on available disk space, mitigating one of the main hassles of SQL databases. Its intended purpose is JSON storage, but any data can be stored.

### Structure
The structure is as follows:

- One KissDB daemon hosts an unlimited number of database objects.
- One KissDB database object holds an unlimited number of table objects.
- One KissDB table object holds an unlimited number of boxes.

A KissDB table object acts like a container of key-value pairs with the name of each box being a key and its contents being the value associated with it.

In this way, I could access the information of a given username using a request such as the one below:

`GET /MyAppliation/Users/ldarling`

Which might return:

`{"success": true, "result": "{\"name\": \"Luke Darling\", \"email\": \"luke@lukedarling.dev\"}"}`

Or, if the box doesn't exist:

`{"success": false, "result": "Box does not exist."}`

### Security
The daemon will eventually implement authentication, but for the moment should be hidden behind a firewall blocking outside access to its bound port. Once authentication is implemented, it should still be proxied via HTTPS using nginx or a similar proxy server. The server must _never_ be placed in the root of an existing web server.


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
##### Example Responses
`{"success":true,"result":"Database successfully created."}`

`{"success":false,"result":"Database already exists."}`

---

#### Create a table
##### Header
`POST /<database>/<table>`
##### Body
N/A
##### Example Responses
`{"success":true,"result":"Table successfully created."}`

`{"success":false,"result":"Table already exists."}`

---

#### Create a box and optionally initialize its content
##### Header
`POST /<database>/<table>/<box>`
##### Body
`[content]`
##### Example Responses
`{"success":true,"result":"Box successfully created."}`

`{"success":false,"result":"Box already exists."}`

---

#### Get a list of all databases on the server
##### Header
`GET /`
##### Body
N/A
##### Example Responses
`{"success":true,"result":["MyApplication1","MyApplication2"]}`

`{"success":true,"result":[]}`

---

#### Get a list of all tables in a given database
##### Header
`GET /<database>`
##### Body
N/A
##### Example Responses
`{"success":true,"result":["Users","Themes"]}`

`{"success":true,"result":[]}`

---

#### Get a list of all boxes in a given database's table
##### Header
`GET /<database>/<table>`
##### Body
N/A
##### Example Responses
`{"success":true,"result":["ldarling","jdoe"]}`

`{"success":true,"result":[]}`

---

#### Get the contents of a given box
##### Header
`GET /<database>/<table>/<box>`
##### Body
N/A
##### Example Responses
`{"success":true,"result":"Hello, world!"}`

`{"success":true,"result":"{\"name\":\"Luke Darling\",\"email\":\"luke@lukedarling.dev\"}"}`

`{"success":false,"result":"Box does not exist."}`

---

#### Update the contents of a given box
##### Header
`POST /<database>/<table>/<box>`
##### Body
`<content>`
##### Example Responses
`{"success":true,"result":"Box successfully updated."}`

---

#### Delete all databases
##### Header
`DELETE /`
##### Body
N/A
##### Example Responses
`{"success":true,"result":"All databases successfully deleted."}`

---

#### Delete a given database
##### Header
`DELETE /<database>`
##### Body
N/A
##### Example Responses
`{"success":true,"result":"Database successfully deleted."}`

---

#### Delete a given database's given child table
##### Header
`DELETE /<database>/<table>`
##### Body
N/A
##### Example Responses
`{"success":true,"result":"Table successfully deleted."}`

---

#### Delete a given database's given child table's box
##### Header
`DELETE /<database>/<table>/<box>`
##### Body
N/A
##### Example Responses
`{"success":true,"result":"Box successfully deleted."}`


### System Requirements
KissDB currently only works on Linux and has only been tested on Ubuntu. I will never create a Windows version, even though it would be very simple to make cross-compatible, simply because Windows is inferior and not worth wasting code on.


### Disclaimer
This software is still in development and may never see a complete production-ready version. This is mainly an exercise for my own learning experience, but may find its way into being used in some of my smaller projects. If you have criticisms, please refrain from complaining to me, but instead place your corrections in the form of a commit. This is an open-source project, after all.
