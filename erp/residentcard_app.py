import datetime

from excel import *
from util import *


class TableColumnDefine:
    def __init__(self, idx, name):
        self.idx = idx
        self.name = name


SERIAL_NO_COLUMN = TableColumnDefine(1, '序号')
NAME_COLUMN = TableColumnDefine(2, '姓名')
PHONE_COLUMN = TableColumnDefine(3, '电话')
REMARK_COLUMN = TableColumnDefine(4, '备注')
SUCCEED_COLUMN = TableColumnDefine(5, '是否领卡')
FAILED_COLUMN = TableColumnDefine(6, '是否失败')

SUMMARY_SHEET_NAME = '汇总'


def validate_xlsx(wb):
    # 验证表头是否正确
    for ws in get_all_worksheets(wb):
        assert get_cell_value(ws, 1, SERIAL_NO_COLUMN.idx) == SERIAL_NO_COLUMN.name, f'{wb.original_path} - {ws.title}'
        assert get_cell_value(ws, 1, NAME_COLUMN.idx) == NAME_COLUMN.name, f'{wb.original_path} - {ws.title}'
        # assert get_cell_value(ws, 1, PHONE_COLUMN.idx) == PHONE_COLUMN.name, f'${wb.original_path} - ${ws.title}'
        # assert get_cell_value(ws, 1, REMARK_COLUMN.idx) == REMARK_COLUMN.name, ws.title
        # assert get_cell_value(ws, 1, SUCCEED_COLUMN.idx) == SUCCEED_COLUMN.name, ws.title


def sort_xlsx(wb):
    def parse_sheet_name(sheet_name: str):
        ss = sheet_name.split('-')
        assert ss
        date = datetime.datetime.strptime('2022.' + ss[0], "%Y.%m.%d")
        address = ss[1]
        operator = '未知' if len(ss) < 3 else ss[2]

        return date, address, operator

    def default_sort_key(title):
        if title == SUMMARY_SHEET_NAME:
            return datetime.datetime.strptime('1970', "%Y")
        date, addr, operator = parse_sheet_name(title)
        return date

    sort_worksheets(wb, lambda x: default_sort_key(x.title))


def remove_summary(wb):
    remove_worksheet_by_name(wb, SUMMARY_SHEET_NAME)


def calc_summary(ws):
    total_count = 0
    succeed_count = 0
    failed_count = 0
    for i in range(2, ws.max_row + 1):
        name = get_cell_value(ws, i, NAME_COLUMN.idx)
        phone = get_cell_value(ws, i, PHONE_COLUMN.idx)
        succeed = get_cell_value(ws, i, SUCCEED_COLUMN.idx)
        failed = get_cell_value(ws, i, FAILED_COLUMN.idx)

        if not name and not phone:
            continue
        elif not name:
            raise ValueError(f'[{ws.title}] ({NAME_COLUMN.name}-{i}) invalid cell {name}')
        # elif not phone:
        #     raise ValueError(f'[{ws.title}] ({PHONE_COLUMN.name}-{i}) invalid cell {phone}')

        total_count = total_count + 1

        if str(succeed).strip() == '1' and str(failed).strip() == '1':
            raise ValueError('invalid content')

        if str(succeed).strip() == '1':
            succeed_count  = succeed_count + 1
        elif str(failed).strip() == '1':
            failed_count = failed_count + 1

    # 标题,总数,成功,失败,未领
    return ws.title, total_count, succeed_count, failed_count, total_count - succeed_count - failed_count


def generate_summary(wb):
    result = parse_worksheets(wb, lambda ws: list(calc_summary(ws)))
    if not result:
        return

    s1 = sum([int(k[1]) for k in result])
    s2 = sum([int(k[2]) for k in result])
    s3 = sum([int(k[3]) for k in result])
    s4 = sum([int(k[4]) for k in result])

    result.append(['', '', '', '', ''])
    result.append(['总计', s1, s2, s3, s4])

    add_worksheet(wb, [
        {
            'sheet_name': SUMMARY_SHEET_NAME,
            'head': ['点位', '总数', '已领数量', '失败数量', '未领数量'],
            'column_dimensions': [30, 10, 10, 10, 10],
            'data': result
        }
    ])


if __name__ == "__main__":
    d = '/Users/kun/Desktop/云文档/市民卡地推项目/市民卡业务-邵祥/2022延安路支行最终数据.xlsx'

    files = list_dir_files(d, ['.xlsx'], ['汇总.xlsx', '绩效.xlsx'])

    for file in files:
        print(f"process excel {file}")
        wb = load_workbook(file)
        remove_summary(wb)
        validate_xlsx(wb)
        generate_summary(wb)
        sort_xlsx(wb)
        save_workbook(wb, file)
