from pymongo import MongoClient, ASCENDING


MongoDB = MongoClient("mongodb://localhost:27017")

nodedb = MongoDB['nodedb']                       # 创建数据库(不存在则创建)
Nodes = nodedb['nodes']                          # 创建集合(不存在则创建)

Nodes.create_index(                              # 设置 host 和 port 复合唯一约束
    [('host', ASCENDING), ('port', ASCENDING)],
    unique=True
)
