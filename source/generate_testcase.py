from main import *
import json

file_name = input("Testcase file name: ")
game_config = main()
with open(f"testcases/{file_name}.json", mode="w") as file:
    json.dump(game_config, file, indent=4)