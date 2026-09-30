import json
import time
import requests

chunks = [
    (0.0, "I need"),
    (0.4, "I need information about"),
    (0.8, "I need information about reimbursement"),
    (1.2, "I need information about reimbursement for international travel"),
]

print("Streaming transcript simulator")
for timestamp, transcript in chunks:
    print(json.dumps({"timestamp": timestamp, "transcript": transcript}))
    try:
        r = requests.post(
            "http://127.0.0.1:5000/api/query",
            json={"query": transcript},
            timeout=60
        )
        print(r.json())
    except Exception as exc:
        print("Start Flask first. Error:", exc)
    time.sleep(0.5)
