# https://www.google.com/search?q=python+show+table&oq=python+show+table&aqs=chrome..69i57j0i512l2j0i22i30l7.3671j0j1&sourceid=chrome&ie=UTF-8
# https://stackoverflow.com/questions/9535954/printing-lists-as-tabular-data

from texttable import Texttable
t = Texttable()
t.add_rows([['Name', 'Age'], ['Alice', 24], ['Bob', 19]])
print(t.draw())
