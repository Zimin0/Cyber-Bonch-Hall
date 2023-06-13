from django.test import TestCase


# from .models import TimePeriod
# from computers.models import Computer

# for i in range(20):
#     Computer.objects.create(ready_to_use=True, number=i+1)

# for k in Computer.objects.all(): 
#     for i in range(7):
#         for j in range(4):
#             if j == 0:
#                 TimePeriod.objects.create(time=f'{16+i}:00', computer=k)
#                 continue
#             TimePeriod.objects.create(time=f'{16+i}:{15*j}', computer=k)


# def compare_two_str_time(time1, time2):
#     time1_s = time1.split(':')
#     time2_s = time2.split(':')
#     if int(time1_s[0]) == int(time2_s[0]):
#         return time1_s[1] > time2_s[1]
#     return time1_s[0] > time2_s[0]


# print(compare_two_str_time('14:20', '15:20'))

