M = 0                                   #互感系数
PI = 3.14
E = 0                                   #感应电压
I = 100                                 #励磁电流
f = 200                                 #频率
i = 0                                   #计数
n = input("n=")                         #总次数
n = int(n)
while i < n:
    E = input("E=")
    E = float(E)
    M = E/(2*PI*f*I)
    print(M)

