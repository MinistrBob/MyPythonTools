list1 = [1, 3, None, 2, 7, None, 4, 9]
print(list1)
not_none_list = filter(None.__ne__, list1)
print(type(not_none_list))
print(not_none_list)
list1 = list(not_none_list)
list1.sort()
print(list1)
