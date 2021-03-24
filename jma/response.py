from datetime import datetime, time

from jma.exceptions import BadCsvException

def try_cast_float(val):
    try:
        return float(val)
    except ValueError:
        return None

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
        timestamp = self.jp_date_to_iso(timestamp)
        values = [try_cast_float(v) for v in values]
        if self.convert_to_kwh:
            # 3.6 MJ/m2 = 1 kWh/m2
            values =  [x/3.6 if x is not None else None for x in values]
        data = [timestamp] + values
        row = dict()
        for i, val in enumerate(data):
            hdr = self.headers[i]
            row[hdr] = val
        self.csv.append(row)

    def jp_date_to_iso(self, text: str):
        """Convert Japanese dates in the format 'yyyy年mm月dd日' to ISO format"""
        dt = datetime.strptime(text, '%Y年%m月%d日')
        return dt.strftime('%Y-%m-%d')


class JmaHourlyIrradiationResponse(JmaIrradiationResponse):
    def jp_date_to_iso(self, text:str):
        """Convert Japanese dates in the format yyyy年mm月dd日H時 to ISO format"""
        split = text.split('日')
        date = datetime.strptime(split[0], '%Y年%m月%d')
        if len(split) > 1 and '時' in split[1]:
            hr = split[1][:split[1].index('時')]
            # jma timestamps are at the END of the period, which causes
            # the first timestamp to start at 1am and the last one to
            # end at 00:00 of the next day. Subtract one to make everything
            # line up in a single 24-hour period
            hr = max(0, int(hr)-1)
        else:
            hr = 0
        t = time(hr, 0)
        dt = datetime.combine(date, t)
        return dt.strftime('%Y-%m-%d %H:%M')

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
    '長野': 'Nagano',
    '長崎': 'Nagasaki',
    '名古屋': 'Nagoya',
    '那覇': 'Naha',
    '大分': 'Oita',
    '佐賀': 'Saga',
    '札幌': 'Sapporo',
    '仙台': 'Sendai',
    '山形': 'Yamagata',
}
