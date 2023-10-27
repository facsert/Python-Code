'''
Author       : facsert
Date         : 2023-08-14 10:43:49
LastEditTime: 2023-09-27 21:19:44
Description  : edit description
'''
from openpyxl import load_workbook, Workbook

class Excel:
    
    def __init__(self, file, mode):
        self.file = file
        self.mode = mode
        self.mode_init()
        
    def __enter__(self):
        return self
    
    def __exit__(self, e_type, e_value, e_tb):
        self.wb.close()
        if any((e_type, e_value, e_tb)):
            raise RuntimeError(f"error: {e_value}\n")
    
    def mode_init(self):
        """ 模式初始化
            'w' 新建 excel 表格 
            'r' 读取 excel 表格
        """
        if self.mode.lower() == 'w':
            self.wb = Workbook()
            self.sheet = self.wb.active
            return
            
        if self.mode.lower() == 'r':
            self.wb = load_workbook(self.file, data_only=True)
            self.sheet = self.wb[self.wb.sheetnames[0]]
            self.head = self.read_head()
            return 
        
        print(f'error mode {self.mode}, select r or w')
        exit()

    def cell_value(self, row, col):
        """ 通过坐标读取值 """
        return self.sheet.cell(row=row, column=col).value
    
    def set_cell(self, row, col, value):
        """ 通过坐标写入值 """
        self.sheet.cell(row, col).value = value
        
    def read_head(self):
        """ 读取表格表头 """
        max_col = self.sheet.max_column + 1
        return [self.cell_value(1, col) for col in range(1, max_col)]
    
    def select_column(self, select, key=None):
        """ 选择属性对应的列 
            select 筛选需要输出的列

        """
        if len(select) == 0:
            select = self.head
            
        if key != None and key not in select:
            print(f"{key} not in {select}")
            exit()
        
        if set(self.head) < set(select):
            print(f'{select} not in {self.head}')
            exit()
        
        return [self.head.index(k) for k in select if k in self.head]
    
    def excel_to_list(self, select=[]):
        """ 读取表格生成列表 
            select 筛选需要读取的列
        """
        indexs = self.select_column(select)
        excel_list = []
        
        for row in range(2, self.sheet.max_row + 1):        
            excel_list.append({
                self.head[col]: self.cell_value(row, col+1) 
                for col in indexs
            })
        return excel_list
        
    def excel_to_dict(self, key, select=[]):
        """ 读取表格生成字典, 一行一个字典
            key 指定改行转成字典的 key
            select 筛选需要输出的键值对
        """
        indexs = self.select_column(select, key)
        excel_dict = {}
        
        for row in range(2, self.sheet.max_row + 1):
            key_value = self.cell_value(row, self.head.index(key) + 1)
            excel_dict.update({key_value: {
                self.head[col]: self.cell_value(row, col+1)
                for col in indexs
            }})
            
        return dict(sorted(excel_dict.items()))
    
    def list_to_excel(self, lst, select=[]):
        """ 列表生成表格 
            lst list[dict]: 字典列表
            select 筛选需要输出的列
        """
        try:
            self.head = list(lst[0].keys())
        except Exception as e:
            print(f"data type error, must list[dict]")
            exit()
            
        indexs = self.select_column(select)
        self.sheet.append([self.head[i] for i in indexs])
        for line in lst:
            self.sheet.append([line[self.head[i]] for i in indexs])

        self.wb.save(self.file)
        
    def dict_to_excel(self, dic, select=[]):
        """字典生成表格
           dic dict[dict]: 双层字典
           select 需要写入表格的键值对
        """
        try:
            self.head = list(list(dic.values())[0].keys())
        except Exception as e:
            print(f"data type error, must dict[str, dict]")
            exit()
            
        indexs = self.select_column(select)
        self.sheet.append([self.head[i] for i in indexs])
        for line in dic.values():
            self.sheet.append([line[self.head[i]] for i in indexs])
            
        self.wb.save(self.file)


if __name__ == '__main__':
    with Excel('excel.xlsx', 'r') as e:
        array = e.excel_to_dict(key="用例编号", select=["用例编号", "用例名称", "执行结果"])
        
    with Excel('save.xlsx', 'w') as e:
        e.dict_to_excel(array, select=["用例编号", "执行结果"])