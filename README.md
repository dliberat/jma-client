# JMA Irradiation Data Client

## About

The Japanese Meteorological Association provides free access to various weather measurements from weather stations across the country through an online portal. However, they do not provide an API.

This client can be used to programmatically download Global Irradiation data from their website.

## Example Usage

```python
from datetime import date
from client import JmaClient, JmaStation

s = date(2020, 12, 31)
e = date(2021, 1, 2)
stations = (JmaStation.Fukuoka, JmaStation.Kagoshima)

with JmaClient() as c:
    response = c.get_irradiation_data(s, e, stations)
    print('\t'.join(response.headers))
    for row in response.csv:
        print('\t'.join([str(row[hdr]) for hdr in response.headers]))
```

Result:
```
Date	Fukuoka	Fukuoka_LT	Kagoshima	Kagoshima_LT
2020-12-31	7.55	7.1	11.16	8.7
2021-01-01	2.53	7.1	9.27	8.6
2021-01-02	1.07	7.1	9.24	8.6
```

## How do I find ID numbers for other JMA stations?

I've only gone through a small subset of all the available stations and included them in the JmaStation enumeration. If you wish to use stations that are not listed here, you will need to add them manually. This can be done by inspecting the request parameters when downloading CSV data from [JMA](https://www.data.jma.go.jp/gmd/risk/obsdl/index.php) using your browser's Developer Tools.