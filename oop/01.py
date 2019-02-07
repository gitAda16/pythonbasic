'''
定义一个学生类，用来形容学生
'''
class Student():
    # 一个孔磊，pass表示直接跳过，pass必须有
    pass
#定义一个对象
xiaohong = Student()

# 描述听Python的学生类
class PythonStudent():
    #属性
    name = None
    age = 18
    course = "Python"
    # 默认有一个self参数
    def doHomeWork(self):
        print("I'm doing homework.")
        return None

yueyue = PythonStudent()
yueyue.doHomeWork()

