from datetime import datetime

from exceptions import BadCsvException


def jp_date_to_iso(text: str):
    """Convert Japanese dates in the format 'yyyy年mm月dd日' to ISO format"""
    dt = datetime.strptime(text, '%Y年%m月%d日')
    return dt.strftime('%Y-%m-%d')


class JmaIrradiationResponse():
    def __init__(self, csv_data: str, kwh=False):
        """
        Args:
            csv_data (str) - CSV data returned from JMA
            kwh (bool) - If true MJ/m2 values will be converted to kWh/m2
        """
        self.headers = []
        self.csv = []
        self.convert_to_kwh = kwh
        try:
            csv_data = csv_data.replace('\r', '') # CRLF -> LF
            self._parse(csv_data)
        except:
            raise BadCsvException(csv_data)

    def _parse(self, csv_data: str):
        for i, line in enumerate(csv_data.split("\n")):
            if i <= 1:
                self._validate_line(i, line)
            elif len(line) < 1:
                continue
            elif line[0] not in '0123456789':
                self._handle_headers(i, line)
            else:
                self._handle_data(i, line)
    
    def _validate_line(self, i: int, line: str):
        if i == 0:
            assert 'ダウンロードした時刻' in line
        elif i == 1:
            assert len(line) == 0

    def _handle_headers(self, i: int, line:str):
        """Header info is divided into two or more lines.
        The first line indicates the station name, the second line indicates the data type
        The header for the date filed is left blank in the CSV data, so we ignore the first
        comma and add the date header manually later

        Example header rows without long term averages:
        ,福岡,佐賀,長崎
        ,合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡)

        Example header rows with long term averages
        ,山口,山口,松江,松江
        ,合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡)
        ,,平年値(MJ/㎡),,平年値(MJ/㎡)
        """
        split = line.split(',')
        if i == 2:
            self.headers = ['Date'] + [station_jp_to_en.get(h, h) for h in split[1:]]
        else:
            for j, data_type in enumerate(split):
                if '平年値' in data_type:
                    self.headers[j] += '_LT' # Long Term Average
    
    def _handle_data(self, i: int, line:str):
        """
        Example data row:
        2021年1月1日,2.53,6.95,5.71
        """
        if len(line) < 1:
            return
        if line[0] not in '0123456789': # all data rows should start with a year (Ex: 2021年)
            return
        split = line.split(',')
        timestamp, values = split[0], split[1:]
        timestamp = jp_date_to_iso(timestamp)
        if self.convert_to_kwh:
            # 3.6 MJ/m2 = 1 kWh/m2
            values =  [float(x)/3.6 if len(x) > 0 else None for x in values]
        else:
             values = [float(x) if len(x) > 0 else None for x in values]
        data = [timestamp] + values
        row = dict()
        for i, val in enumerate(data):
            hdr = self.headers[i]
            row[hdr] = val
        self.csv.append(row)


station_jp_to_en = {
    '秋田': 'Akita',
    '青森': 'Aomori',
    '福岡': 'Fukuoka',
    '広島': 'Hiroshima',
    '鹿児島': 'Kagoshima',
    '熊本': 'Kumamoto',
    '松江': 'Matsue',
    '宮崎': 'Miyazaki',
    '盛岡': 'Morioka',
    '長崎': 'Nagasaki',
    '那覇': 'Naha',
    '大分': 'Oita',
    '佐賀': 'Saga',
    '札幌': 'Sapporo',
    '仙台': 'Sendai',
    '山形': 'Yamagata',
}
