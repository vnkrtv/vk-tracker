db.createUser(
    {
        user  : "MONGO_USER",
        pwd   : "MONGO_PWD",
        roles : [
            {
                role : "readWrite",
                db   : "MONGO_DBNAME"
            }
        ]
    }
)
