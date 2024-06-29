# client.py

import grpc
from pb.user_pb2 import UserName, Null
from pb.user_pb2_grpc import UserHandleStub

def main():
    with grpc.insecure_channel("localhost: 50051") as channel:
        stub = UserHandleStub(channel)
        user_list = stub.GetUserList(Null())
        for i in user_list.userlist:
            print(i.name, i.age, i.hobby)
        
        user = stub.GetUser(UserName(name="John"))
        print(user)

if __name__ == '__main__':
    main()