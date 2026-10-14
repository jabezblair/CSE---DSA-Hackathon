import csv

def read_csv(path):
    with open(path, newline='') as f:
        return [row for row in csv.reader(f) if row]

def write_csv(path, rows):
    with open(path, 'w', newline='') as f:
        csv.writer(f).writerows(rows)