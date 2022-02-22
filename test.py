# 郑淋文
# 时间: 2022/2/18 10:07
import time
a = 3
b = 1
count = 0
# print(b<2)
# print(a>8)

timeout = 3
timeout_start = time.time()
# print(timeout_start)
while b>-10 and a>2 and time.time()<timeout+timeout_start:
    b -= 1
    count+=1
print(count)
print(b)