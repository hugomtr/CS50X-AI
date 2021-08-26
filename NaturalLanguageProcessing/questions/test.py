dicto = { "1":{"key1":3,"key2":12},"2":{"key1":3,"key2":3}}

dicto = dict(sorted(dicto.items(),key=lambda item: (item[1]["key1"],item[1]["key2"])))
print(dicto)