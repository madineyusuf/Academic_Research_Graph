import json

with open("data/academics_sample.json", "r",
        encoding="utf-8") as file:

    academics = json.load(file)

print("Toplam akademisyen:", len(academics))

for academic in academics:
    print("-------------------")
    print(academic["name"])
    print(academic["title"])
    print(academic["country"])
    print(academic["university"])
    print(academic["department"])
    print(academic["fields"])
    print("-------------------")