list = ["1", "6", "7", "8", "9"]
#print(list)
dict = {"negas": ["1", "2", "3", "4"]}
list2 = ["1", "A", "B", "C" ]
parent = "negas"
find = "9"
#list[1:2] = dict[parent]
position = list.index(find)
#print(position)
if position+1 != len(list):
    del list[position] # PARA BORRAR EL LOOP QUE SE DUPLICA
    list[position:1] = list2
else:# en caso que sea la ultima pos
    #print("aqui")
    del list[position] # PARA BORRAR EL LOOP QUE SE DUPLICA
    list[position:1] = list2
#print(list)
assert sum([1, 2, 3]) == 6, "Should be 6"
assert sum([1, 1, 1]) == 6, "Should be 6"