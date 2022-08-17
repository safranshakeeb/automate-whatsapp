from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://Safran:Hijabsafran@786!!@cluster0.3v1x4.mongodb.net/?retryWrites=true&w=majority")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", " ")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        res.message("Hi welcome to pearl threading salon.\nWhat do you want to know\n\n"
                    "1️⃣ Our services\n2️⃣ Price list\n3️⃣ Contact details\n4️⃣ Book your appointment")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 1:
            res.message("You can contact us through phone or e-mail. \n *Phone*: 13213 \n *E-mail: salt*")
        elif option == 2:
            res.message("You have entered *ordering mode*.")
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            res.message("You can select from below \n Next agu kara ge na")
        elif option == 3:
            res.message(" We work everyday from *9 am to 9 pm*")
        elif option == 4:
            res.message("51310")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("please enter a valid response")
            return str(res)
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message("What do you want to know \n\n1️⃣ Our services\n2️⃣ Price list\n3️⃣ Contact Details\n4️⃣ Book "
                        "your appointment")
        elif 1 <= option <= 9:
            cakes = ["1", "2", "3", "4"]
            selected = cakes[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})
            res.message("Excellent Choice😍")
            res.message("Please enter your address to confirm the order")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thanks for shopping with us!")
        res.message(f"Your order for {selected} has been received and will be delivered within an hour.")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message("Hi welcome to pearl threading salon again.\nWhat do you want to know\n\n"
                    "1️⃣ Our services\n2️⃣ Price list\n3️⃣ Contact details\n4️⃣ Book your appointment")
        users.update_one({"number": number}, {"$set": {"status": "main"}})

    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)


if __name__ == "__main__":
    app.run(port=5000)
