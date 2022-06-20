import datetime
import json
import sqlite3
from time import sleep
from typing import Any

import discord

json_data = json.load(open("settings.json"))


class NotDbManager:
    def __init__(self, filename: str) -> None:
        self.__data = None
        self.__filename = filename
        self.read()
    
    def __str__(self) -> str:
        return str(self.__filename)

    def read(self) -> None:
        try:
            egg = open(self.__filename, "r").read()
        except FileNotFoundError:
            raise ValueError("DB file is not found")
        if type(self.__data) != dict:
            self.__data = dict()
        for i in egg.split("\n"):
            tempvar = i.split(" - ")
            try:
                self.__data.update({tempvar[0]: tempvar[1]})
            except IndexError:
                pass

    def write(self) -> None:
        file = open(self.__filename, "w")
        egg = "\n".join(map(lambda x: f"{x} - {self.__data[x]}", self.__data.keys()))
        file.write(egg)
        file.close()
    
    def get(self, key: str) -> Any:
        try:
            return self.__data[key]
        except KeyError:
            return None

    def set(self, key: str, value: Any) -> None:
        if "-" in key or "-" in value:
            raise ValueError("Incorrect key or value")
        self.__data.update({key: value})


def embed_builder(title: str, *, desc: str = None,
                  color: discord.Colour = discord.Colour.green()): return discord.Embed(title=title, description=desc,
                                                                                        color=color)

def create_log(message: str, code: str = "ok", logged: bool = True):
    out = f"[{code.upper()}][{str(datetime.datetime.now())[:19]}]: {message}"
    print(out)

    if logged:
        with open(f"logs/log_{datetime.date.today()}.txt", "a", encoding="UTF-8") as file:
            file.write("\n" + out)

def do_to_database(command: str, *options):
    dbFilename = json_data["db"]
    while True:
        try:
            conn = sqlite3.connect(dbFilename, timeout=1)
            cursor = conn.cursor()
            if options == []:
                returnStr = list(cursor.execute(command))
            else:
                returnStr = list(cursor.execute(command, options))
            conn.commit()
            cursor.close()
            conn.close()
            return returnStr
        except sqlite3.OperationalError as e:
            create_log(e, code="error")
            sleep(1)
            continue
