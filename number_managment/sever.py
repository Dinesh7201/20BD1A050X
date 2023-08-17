import requests
from flask import Flask, request, jsonify
import json
import gevent
from gevent import monkey
monkey.patch_all()

app = Flask(__name__)

def fetch_numbers(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            try:
                data = response.json()
                return data.get('numbers', [])
            except json.JSONDecodeError:
                print(f"Invalid JSON response from {url}")
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
    return []

@app.route('/numbers', methods=['GET'])
def get_numbers():
    urls = request.args.getlist('url')
    
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400
    
    jobs = [gevent.spawn(fetch_numbers, url) for url in urls]
    gevent.joinall(jobs, timeout=0.5)
    
    merged_numbers = set()
    for job in jobs:
        numbers = job.value
        if numbers is not None:
            merged_numbers.update(numbers)
    
    return jsonify({"numbers": sorted(list(merged_numbers))})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008)
