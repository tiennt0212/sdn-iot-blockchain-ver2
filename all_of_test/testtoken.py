#!/usr/bin/env python3
import tokenlib
# info={
#         "deviceId":12,
#     }
# manager=tokenlib.TokenManager(secret="OCEANSONG")
# token=manager.make_token(info)

# print("Token is: \n\t{}\n".format(token))

# data=tokenlib.parse_token(
#     token,
#     secret="OCEANSONG"
# )
# print("Data parse from token is:\n\t{}\n".format(data))

# # dataFuture=tokenlib.parse_token(
# #     token,
# #     secret="OCEANSONG",
# #     now=12345678999
# # )#Token has expired
# # print("Data parse from token is:\n\t{}\n".format(dataFuture))


token = "eyJkZXZpY2VJZCI6IDEyLCAic2FsdCI6ICJiOTVkNWQiLCAiZXhwaXJlcyI6IDE2MjY5MTc4NzYuMzE5OTM2M304g0csktCEakP_f6ksZnKmxjLAp9cJTaPaklxtjSCSQg=="
manager = tokenlib.TokenManager(secret="OCEANSONG")
newtoken = manager.make_token({"name":"Nguyen Thanh Tien"})
data=None
try:
    data=manager.parse_token(token)
    print(data)
except:
    print("Error")

if(data['expires']): print ("Good")
else: print("Expired")