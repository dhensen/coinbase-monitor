import csv
import os
from typing import Any, List, Tuple


class DataRecorder:
    def __init__(self, data_slug) -> None:
        self.filename = f'{data_slug}.csv'

        if os.path.getsize(self.filename) == 0:
            self.add_header()

    def add_header(self):
        with open(self.filename, mode='a', newline='') as f:
            record_writer = csv.writer(f)  # defaults CSV
            record_writer.writerow([
                'timestamp', 'token_name', 'amount', 'staked_amount',
                'eur_price', 'total_amount', 'total_eur_amount'
            ])

    def add_record(self, timestamp, token_name, eur_price, amount,
                   staked_amount, total_amount, total_eur_amount):
        with open(self.filename, mode='a', newline='') as f:
            record_writer = csv.writer(f)  # defaults CSV
            record_writer.writerow([
                timestamp, token_name, amount, staked_amount, eur_price,
                total_amount, total_eur_amount
            ])


class DataReader:
    def __init__(self, data_slug) -> None:
        self.filename = f'{data_slug}.csv'

    def get_records(self) -> Tuple[List[Any], List[List[Any]]]:
        with open(self.filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            data = [row for row in reader]
            return headers, data
