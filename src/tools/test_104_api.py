import requests
import json

def test_api():
    # Attempting the endpoint found earlier
    url = "https://www.104.com.tw/jobs/search/list" # Try 'list' not 'api/jobs/list' first, or try exact intercept
    # The intercept said: jobs/search/api/jobs/list ?
    # Let's try matching the intercept pattern I saw
    # https://www.104.com.tw/jobs/search/api/jobs/list
    
    url = "https://www.104.com.tw/jobs/search/api/jobs/list"
    
    params = {
        "ro": "0",
        "keyword": "Java",
        "jobsource": "index_s",
        "mode": "s",
        "order": "11",
        "page": "1"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.104.com.tw/jobs/search/",
        "Accept": "application/json"
    }
    
    print(f"Testing URL: {url}")
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"URL: {resp.url}")
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                print("JSON Parsed Successfully")
                if "data" in data and "list" in data["data"]:
                    jobs = data['data']['list']
                    print(f"Jobs Found: {len(jobs)}")
                    if len(jobs) > 0:
                        print(f"First: {jobs[0].get('jobName')}")
                else:
                    print(f"Keys: {data.keys()}")
            except:
                print("Response is not JSON")
                print(resp.text[:200])
        else:
            print("Error Response:")
            print(resp.text[:200])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
