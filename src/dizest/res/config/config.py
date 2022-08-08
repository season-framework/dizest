import os
import dizest

spawner_class = dizest.spawner.SudoSpawner

def cwd(user_id):
    return "/" + os.path.join("home", user_id)
