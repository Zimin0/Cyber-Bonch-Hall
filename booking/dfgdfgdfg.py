import time 


now_struct = time.localtime() # now in struct
hours = now_struct.tm_hour * 60 * 60 # часы в секундах
minutes = now_struct.tm_min * 60 # минуты в секундах
seconds = now_struct.tm_sec

print(hours + minutes + seconds)
print(now_struct.tm_hour)