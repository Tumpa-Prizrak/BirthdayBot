from helper import NotDbManager

notdb = NotDbManager("notdb.txt")
print(notdb.get("token"))
notdb.set("token", "-")
notdb.write()