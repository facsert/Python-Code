# server

import grpc
from concurrent import futures
from pb.user_pb2_grpc import UserHandleServicer, add_UserHandleServicer_to_server
from pb.user_pb2 import UserList, User

users = [
    {"name": "John", "age": 16, "hobby": "soccer"},
    {"name": "Lily", "age": 18, "hobby": "tennis"},
    {"name": "Jack", "age": 20, "hobby": "basketball"}
]

class UserService(UserHandleServicer):

    def AddUser(self, request, context):
        user_list = UserList()
        user_list.userlist.extend([*users, request])
        return user_list

    def GetUser(self, request, context):
        for p in users:
            if p["name"] == request.name:
                return User(name=request.name, age=p["age"], hobby=p["hobby"])
        return User(name="nobody", age=0, hobby="no")

    def GetUserList(self, request, context):
        response = UserList(userlist=[
            User(name=p['name'], age=p['age'], hobby=p['hobby'])
            for p in users
        ])
        return response

def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_UserHandleServicer_to_server(UserService(), server)
    server.add_insecure_port("localhost:50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    main()
