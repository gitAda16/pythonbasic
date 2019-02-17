# class Myt:
#     def __init__(self, over=False):
#         self.over = over
#
# class Yt1:
#     def __init__(self, over=False):
#         self.over = over
#
#     @property
#     def my(self):
#         return Myt(self.over)
#
#     def change(self):
#         self.over = not self.over
#
#     def printid(self):
#         print(id(self.my))
#
# y = Yt1()
# print(y.my.over)
# y.over = True
# print(id(y.over))
# y.printid()
# y.printid()
# print(y.my.over)

t = list()
t.append((1,2))
print(t)

s = tuple([1,2])
t.remove(s)
print(t)