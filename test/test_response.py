"""Test cases for responses"""
import unittest
from response import JmaIrradiationResponse, jp_date_to_iso

class TestJpDateConversion(unittest.TestCase):
    def test_january(self):
        dt = jp_date_to_iso('2021年1月6日')
        self.assertEqual('2021-01-06', dt)

    def test_december(self):
        dt = jp_date_to_iso('2020年12月31日')
        self.assertEqual('2020-12-31', dt)


class TestJmaIrradiationResponse(unittest.TestCase):
    def setUp(self):
        self.csv_data = '''ダウンロードした時刻：2021/01/10 15:53:37

,福岡,佐賀,長崎
,合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡)
2021年1月1日,2.53,6.95,5.71
2021年1月2日,1.07,3.56,4.54
2021年1月3日,11.01,11.68,10.94
2021年1月4日,12.33,12.31,11.71
2021年1月5日,6.30,5.02,5.27
2021年1月6日,5.45,5.58,5.04
'''
        self.csv_data_with_lta = '''ダウンロードした時刻：2021/01/11 00:34:52

,盛岡,盛岡,秋田,秋田
,合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡)
,,平年値(MJ/㎡),,平年値(MJ/㎡)
2021年1月1日,4.01,5.9,2.46,4.0
2021年1月2日,8.16,5.9,2.44,4.0
'''

        self.csv_data_incomplete = '''ダウンロードした時刻：2021/01/10 23:54:52

,山口,山口,松江,松江
,合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡),合計全天日射量(MJ/㎡)
,,平年値(MJ/㎡),,平年値(MJ/㎡)
2021年1月1日,,,5.85,
2021年1月2日,,,3.58,
'''

    def test_parse_headers(self):
        response = JmaIrradiationResponse(self.csv_data)
        expected = ['Date', 'Fukuoka', 'Saga', 'Nagasaki']
        self.assertListEqual(expected, response.headers)

    def test_parse_headers_lta(self):
        response = JmaIrradiationResponse(self.csv_data_with_lta)
        expected = ['Date', 'Morioka', 'Morioka_LT', 'Akita', 'Akita_LT']
        self.assertListEqual(expected, response.headers)

    
    def test_parse_data(self):
        response = JmaIrradiationResponse(self.csv_data)
        expected = [
            [2.53, 6.95, 5.71],
            [1.07, 3.56, 4.54],
            [11.01, 11.68, 10.94],
            [12.33, 12.31, 11.71],
            [6.30, 5.02, 5.27],
            [5.45, 5.58, 5.04],
        ]
        for i, row in enumerate(response.csv):
            self.assertAlmostEqual(row['Fukuoka'], expected[i][0], 3)
            self.assertAlmostEqual(row['Saga'], expected[i][1], 3)
            self.assertAlmostEqual(row['Nagasaki'], expected[i][2], 3)

    def test_parse_data_lta(self):
        response = JmaIrradiationResponse(self.csv_data_with_lta)
        expected = [
            [4.01, 5.9, 2.46, 4.0],
            [8.16, 5.9, 2.44, 4.0],
        ]
        for i, row in enumerate(response.csv):
            self.assertAlmostEqual(row['Morioka'], expected[i][0], 3)
            self.assertAlmostEqual(row['Morioka_LT'], expected[i][1], 3)
            self.assertAlmostEqual(row['Akita'], expected[i][2], 3)
            self.assertAlmostEqual(row['Akita_LT'], expected[i][3], 3)
  
    def test_parse_data_kwh(self):
        response = JmaIrradiationResponse(self.csv_data, kwh=True)
        expected = [
            [0.70277, 1.930555555, 1.58611],
            [0.29722, 0.988888, 1.2611],
            [3.058333, 3.2444, 3.0388],
            [3.425, 3.41944, 3.2527],
            [1.75, 1.39444, 1.46388],
            [1.513888, 1.55, 1.4]
        ]
        for i, row in enumerate(response.csv):
            self.assertAlmostEqual(row['Fukuoka'], expected[i][0], 3)
            self.assertAlmostEqual(row['Saga'], expected[i][1], 3)
            self.assertAlmostEqual(row['Nagasaki'], expected[i][2], 3)

    def test_parse_data_lta_kwh(self):
        response = JmaIrradiationResponse(self.csv_data_with_lta, kwh=True)
        expected = [
            [1.113888, 1.638888, 0.68333, 1.11111],
            [2.266666, 1.638888, 0.67777, 1.11111],
        ]
        for i, row in enumerate(response.csv):
            self.assertAlmostEqual(row['Morioka'], expected[i][0], 3)
            self.assertAlmostEqual(row['Morioka_LT'], expected[i][1], 3)
            self.assertAlmostEqual(row['Akita'], expected[i][2], 3)
            self.assertAlmostEqual(row['Akita_LT'], expected[i][3], 3)

    def test_parse_dates(self):
        response = JmaIrradiationResponse(self.csv_data)
        dates = [row['Date'] for row in response.csv]
        for i, date in enumerate(dates):
            self.assertEqual(f'2021-01-{i+1:02}', date)

    def test_parse_data_incomplete_kwh(self):
        response = JmaIrradiationResponse(self.csv_data_incomplete, kwh=True)
        row0 = response.csv[0]
        row1 = response.csv[1]
        self.assertAlmostEqual(row0['Matsue'], 1.624999, 3)
        self.assertAlmostEqual(row1['Matsue'], 0.994444, 3)
        self.assertIsNone(row0['Matsue_LT'])
        self.assertIsNone(row1['Matsue_LT'])
        self.assertIsNone(row0['山口'])
        self.assertIsNone(row1['山口'])
        self.assertIsNone(row0['山口_LT'])
        self.assertIsNone(row1['山口_LT'])
