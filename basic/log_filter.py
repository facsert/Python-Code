# 日志解析
import csv
from datetime import datetime
from re import search
from collections import defaultdict

class LogParse:
    
    def __init__(self, file_name):
        self.name = file_name
        self.repeat_timestamp = defaultdict(list)
        self.fuzzy_timestamp = defaultdict(list)
        self.repeat_logcount = defaultdict(int)
        self.fuzzy_logcount = defaultdict(int)
        self.repeat_cache = {}
        self.fuzzy_cache = {}
        self.counter = defaultdict(int)
    
    def read_file(self):
        heads = ['filename', 'filter', 'level', 'timestamp', 'index', 'count', 'log']
        self.csv = csv.DictWriter(open(f'{self.name}.csv', 'w', newline=''), fieldnames=heads)
        fp = open(self.name, 'r', encoding='utf8')
        [self.log_parse(line) for line in fp]
        self.csv.close()
        fp.close()

    def log_parse(self, line):
        """ 自定义 log 解析 """
        self.timestamp = datetime.strptime(line[11:30], '%Y-%m-%d %H:%M:%S')
        self.level, self.msg = line[1:9], line[34:]
        self.blacklist(line)
        self.whitelist(line)
        self.slice_repeat(line, 5, 3)
        self.fuzzy_repeat(line, '[GET]',5, 3)
        
    def slice_repeat(self, line, time_threshold, count_threshold):
        """ 筛选在 time_threshold 时间内, 出现超过 count_threshold 次的 log """
        
        # 删除不在时间片段内的 log, 并对 log 重新计数
        for old_timestamp in self.repeat_timestamp:
            if (self.timestamp - old_timestamp).seconds < time_threshold:
                continue
            
            for item in self.repeat_timestamp[old_timestamp]:
                self.repeat_logcount[item[34:]] -= 1
        
        # 合并相同时间点 log, 并对 log 计数
        self.repeat_timestamp[self.timestamp].append(line)
        self.repeat_logcount[self.msg] += 1
        
        if self.repeat_logcount[self.msg] >= count_threshold:
            if self.repeat_cache.get(self.msg, None) is None:
                self.repeat_cache[self.msg] = {'filename': self.name, 'level': self.level, 
                    'count': self.repeat_logcount[self.msg], 'log': [line],
                    'start': self.timestamp, 'close': self.timestamp,
                }
            else:
                self.repeat_cache[self.msg]['log'].append(line)
                self.repeat_cache[self.msg]['close'] = self.timestamp
                self.repeat_cache[self.msg]['count'] += 1

    def fuzzy_repeat(self, line, regex, time_threshold, count_threshold):
        """ log 包含模糊匹配内容, 并在 time_threshold 时间内, 出现超过 count_threshold 次 """
        match = search(regex, line)
        if match is None:
            return

        for old_timestamp in self.fuzzy_timestamp:
            if (self.timestamp - old_timestamp).seconds > time_threshold:
                self.fuzzy_logcount[regex] -= len(self.fuzzy_timestamp[old_timestamp])

        self.fuzzy_timestamp[self.timestamp].append(line)
        self.fuzzy_logcount[regex] += 1
        
        if self.fuzzy_logcount[regex] >= count_threshold:
            if self.repeat_cache.get(regex, None) is None:
                self.repeat_cache[regex] = {'filename': self.name, 'level': self.level, 
                    'count': self.fuzzy_logcount[regex], 'log': [line],
                    'start': self.timestamp, 'close': self.timestamp,
                }
            else:
                self.repeat_cache[regex]['log'].append(line)
                self.repeat_cache[regex]['close'] = self.timestamp
                self.repeat_cache[regex]['count'] += 1

    def write_repeat(self):
        """ repeat log 写入 csv 文件 """
        for content, item in self.repeat_cache.items():
            self.counter['repeat'] += 1
            self.csv.writerow({
                'filename': item['filename'], 'filter': 'Repeat', 'level': item['level'], 
                'count': item['count'], 'index': self.counter['repeat'],
                'timestamp': f"{item['start']} {item['close']}", 'log': content,
            })
                
    def blacklist(self, line, blacks):
        """ log 存在黑名单内容 """
        for key in blacks:
            if key in line:
                self.counter['blacklist'] += 1
                self.csv.writerow({
                    'filename': self.name, 'filter': 'Blacklist', 'level': self.level, 
                    'count': 1, 'index': self.counter['blacklist'],
                    'timestamp': self.timestamp, 'log': line,
                })
                return
            
    def whitelist(self, line, whits):
        """ log 不包含白名单任意内容 """
        if not any([key in line for key in whits]):
            self.counter['whitelist'] += 1
            self.csv.writerow({
                'filename': self.name, 'filter': 'Whitelist', 'level': self.level, 
                'count': 1, 'index': self.counter['whitelist'],
                'timestamp': self.timestamp, 'log': line,
            })
    
    def fuzzy_match(self, line, regex):
        """ log 包含模糊匹配内容 """
        match = search(regex, line)
        if match is not None:
            self.counter['fuzzy_match'] += 1
            self.csv.writerow({
                'filename': self.name, 'filter': 'Fuzzy Match', 'level': self.level, 
                'count': 1, 'index': self.counter['fuzzy_match'], 'log': line
            })
            

        