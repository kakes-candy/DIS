import pprint, xlrd


path = "SGGZ_9_0\Docs\helpbestand voor definitions.xlsx"


def read_format_defs(path, sheet):

    wb = xlrd.open_workbook(path)

    sheet = wb.sheet_by_name(sheet)

    keys = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]

    dict_list = []
    for row_index in range(1, sheet.nrows):
        d = {
            keys[col_index]: str(sheet.cell(row_index, col_index).value).replace(
                ".0", ""
            )
            for col_index in range(sheet.ncols)
        }
        dict_list.append(d)

    return dict_list


pprint.pprint(read_format_defs(path=path, sheet="pakbon.txt"))
