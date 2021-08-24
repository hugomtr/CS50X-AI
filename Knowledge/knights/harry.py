from logic import *

people = ["Gilderoy", "Pomona", "Minerva", "Horace"]
houses = ["Gryffondor", "Poufssoufle", "Serpentard", "Serdaigle"]

symbols = []

knowledge = And()

for person in people:
  for house in houses:
    symbols.append(Symbol(f"{person}{house}"))

for person in people:
  knowledge.add(Or(
    Symbol(f"{person}Gryffondor"),
    Symbol(f"{person}Poufssoufle"),
    Symbol(f"{person}Serpentard"),
    Symbol(f"{person}Serdaigle")
  ))

 # Each person belongs to a house
for person in people:
  for h1 in houses:
    for h2 in houses:
      if h1 != h2:
        knowledge.add(
          Implication(Symbol(f"{person}{h1}"), Not(Symbol(f"{person}{h2}")))
        ) 


# Each house have one person
for house in houses:
  for p1 in people:
    for p2 in people:
      if p1 != p2:
        knowledge.add(
          Implication(Symbol(f"{p1}{house}"), Not(Symbol(f"{p2}{house}")))
        )

knowledge.add(
  Or(Symbol("GilderoyGryffondor"),Symbol("GilderoySerdaigle"))
)
knowledge.add(Not(Symbol("PomonaSerpentard")))
knowledge.add((Symbol("MinervaGryffondor")))


for symbol in symbols:
  if model_check(knowledge,symbol):
    print(symbol)

