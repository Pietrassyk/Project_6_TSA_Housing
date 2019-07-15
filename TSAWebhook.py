from flask import Flask, Response, jsonify ,request
from flask_assistant import Assistant, tell, ask, response
import json
import os

app = Flask(__name__)
assist = Assistant(app, project_id = "burgerstore-wrkkut")


#Intent names
demo = "Demo"
makeburger = "MakeBurger"

def store_json_input(filename = "output.json", how="w"):
    data = request.get_json(force=True)
    dirName = "temp/" + data["session"].split("/")[-1]
    filename = dirName + "/" + data["responseId"] + ".json"
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        print("Directory ", dirName, " Created ")
    else:
        print("Directory ", dirName, " already exists")
    with open(filename, how) as f:
        json.dump(data, f)


@assist.action(demo)
def hello_world():
    store_json_input()
    speech = "Guten Tag, der Herr"
    #print(app.__dict__)
    return tell(f"{speech}!")

@assist.action(makeburger)
def burger_order(Toppings , Cheese, cookgrade):
    store_json_input()
    return tell(f"I will make a burger with {Cheese} and {' and '.join(Toppings) if len(Toppings) >1 else Toppings[0]} and the meat {cookgrade} , is that right Sweety ?")

if __name__ == "__main__":
    app.run("localhost", 8000)