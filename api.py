import csv

from sanic import Sanic
from sanic.response import json
from recorder import DataReader

app = Sanic("staking-stats")

wonderland_time_reader = DataReader('wonderland-time-staking-stats')


@app.route('/')
async def test(request):
    return json({'data': get_data('wonderland-time-staking')})


def get_data(slug):
    if slug == 'wonderland-time-staking':
        headers, data = wonderland_time_reader.get_records()
        series = {key: [] for key in headers}
        for row in data:
            for i, key in enumerate(headers):
                series[key].append(row[i])

        return {
            'wonderland-time-staking': {
                'headers': headers,
                'data': data[::-1],
                'series': series
            }
        }

    return {'undefined': []}


if __name__ == '__main__':
    app.run()
