# JMA Irradiation Data Client

## About

The Japanese Meteorological Association provides free access to various weather measurements from weather stations across the country through an online portal. However, they do not provide an API.

This client can be used to programmatically download Global Irradiation data from their website.

## Installation

```
$ pip install jma-client
```

## Example Usage

### Download daily irradiation data

```python
from datetime import date
from jma import JmaClient, JmaStation

s = date(2020, 12, 31)
e = date(2021, 1, 2)
stations = (JmaStation.Fukuoka, JmaStation.Kagoshima)

with JmaClient() as c:
    response = c.get_daily_irradiation(s, e, stations)
    print('\t'.join(response.headers))
    for row in response.csv:
        print('\t'.join([str(row[hdr]) for hdr in response.headers]))
```

Result:
```
Date	Fukuoka	Kagoshima
2020-12-31	7.55	11.16
2021-01-01	2.53	9.27
2021-01-02	1.07	9.24
```

### Download hourly irradiation data

```python
from datetime import date
from jma import JmaClient, JmaStation

target_date = date(2021, 2, 23)
stations = [JmaStation.Nagano]
with JmaClient() as c:
    response = c.get_hourly_irradiation(target_date, target_date, stations)
    print('\t'.join(response.headers))
    for row in response.csv:
        print('\t'.join([str(row[hdr]) for hdr in response.headers]))
```

Result:
```
Date	Nagano
2021-02-23 00:00	None
2021-02-23 01:00	None
2021-02-23 02:00	None
2021-02-23 03:00	None
2021-02-23 04:00	None
2021-02-23 05:00	0.0
2021-02-23 06:00	0.03
2021-02-23 07:00	0.43
2021-02-23 08:00	1.14
2021-02-23 09:00	2.03
...(contd.)
```

### Download daily irradiation data alongside average long-term values

```python
from datetime import date
from jma import JmaClient, JmaStation

s = date(2021, 2, 1)
e = date(2021, 2, 14)
stations = [JmaStation.Aomori, JmaStation.Morioka]
with JmaClient() as c:
    response = c.get_daily_irradiation(s, e, stations, lta=True)
    print('\t'.join(response.headers))
    for row in response.csv:
        print('\t'.join([str(row[hdr]) for hdr in response.headers]))
```

Response:

```
Date	Aomori	Aomori_LT	Morioka	Morioka_LT
2021-02-01	9.43	6.3	10.88	8.5
2021-02-02	3.81	6.4	6.73	8.7
2021-02-03	4.4	6.5	8.95	8.8
2021-02-04	3.17	6.6	4.96	8.9
2021-02-05	5.11	6.7	10.63	9.0
2021-02-06	4.11	6.8	5.03	9.1
2021-02-07	4.77	6.9	4.88	9.2
2021-02-08	5.41	6.9	12.47	9.3
2021-02-09	4.82	7.0	12.16	9.4
2021-02-10	4.6	7.1	8.67	9.4
2021-02-11	7.35	7.2	10.9	9.5
2021-02-12	13.98	7.3	14.45	9.6
2021-02-13	14.4	7.5	12.58	9.7
2021-02-14	11.59	7.6	13.75	9.8
```

## How do I find ID numbers for other JMA stations?

I've only gone through a small subset of all the available stations and included them in the JmaStation enumeration. If you wish to use stations that are not listed here, you will need to add them manually. This can be done by inspecting the request parameters when downloading CSV data from [JMA](https://www.data.jma.go.jp/gmd/risk/obsdl/index.php) using your browser's Developer Tools.