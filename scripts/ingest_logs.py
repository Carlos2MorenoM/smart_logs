import re
import json
import requests
from datetime import datetime
import hashlib

# --- Configuration ---
# Defines the location of the raw log file and the target API endpoint.
LOG_FILE_PATH = 'data/raw/Linux_2k.log'
API_ENDPOINT = 'http://log_ingestor:8000/ingest'
CURRENT_YEAR = datetime.now().year

def generate_log_id(log_data):
    """
    Creates a hash SHA256 of the log data to be used as unique ID
    Makes sure JSON is sorted so hash is the same always
    """
    # Convert dict in a JSON string, sorting keys
    dhash = hashlib.sha256()
    encoded_log = json.dumps(log_data, sort_keys=True).encode()
    dhash.update(encoded_log)
    return dhash.hexdigest()

def parse_log_line(line):
    """
    Parses a single log line using a regex to extract key fields,
    then combines date/time components into a single ISO 8601 timestamp.
    """
    log_pattern = re.compile(
        r'^(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+'
        r'(?P<hostname>\S+)\s+'
        r'(?P<component>.+?):\s+'
        r'(?P<message>.*)$'
    )

    match = log_pattern.match(line)
    if not match:
        return None

    log_data = match.groupdict()

    try:
        # Create a combined date string and convert it to a datetime object.
        date_str = f"{log_data['month']} {log_data['day']} {CURRENT_YEAR} {log_data['time']}"
        dt_object = datetime.strptime(date_str, '%b %d %Y %H:%M:%S')

        # Format the datetime object into the preferred ISO 8601 format.
        iso_timestamp = dt_object.strftime('%Y-%m-%dT%H:%M:%SZ')

        structured_log = {
            "timestamp": iso_timestamp,
            "hostname": log_data['hostname'],
            "component": log_data['component'],
            "message": log_data['message'].strip()
        }
        return structured_log

    except ValueError as e:
        print(f"⚠️  Date processing error for line: {line.strip()}. Error: {e}")
        return None


def send_log_to_api(log_json):
    """
    Sends a structured log (JSON) to the ingestor API via an HTTP POST request.
    """
    try:
        response = requests.post(API_ENDPOINT, json=log_json, headers={'Content-Type': 'application/json'})
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        print(f"✅ Log sent successfully: {log_json['timestamp']}")
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")


# --- Main Execution Block ---
# Reads the log file line by line, parses each valid line,
# and sends the structured data to the API.
if __name__ == "__main__":
    print(f"🚀 Starting log ingestion from '{LOG_FILE_PATH}'...")
    line_count = 0
    parsed_count = 0
    skipped_count = 0

    try:
        with open(LOG_FILE_PATH, 'r') as file:
            for line in file:
                line_count += 1
                if not line.strip():
                    skipped_count += 1
                    continue

                parsed_log = parse_log_line(line)

                if parsed_log:
                    parsed_count += 1
                    log_id = generate_log_id(parsed_log)
                    parsed_log['log_id'] = log_id
                    send_log_to_api(parsed_log)
                else:
                    skipped_count += 1
                    print(f"⚠️  Line skipped (format mismatch): {line.strip()}")

    except FileNotFoundError:
        print(f"🚨 Error: Log file not found at '{LOG_FILE_PATH}'")
    except Exception as e:
        print(f"🚨 An unexpected error occurred: {e}")

    print("\n" + "="*30)
    print("🏁 Ingestion process finished.")
    print(f"    - Total lines read: {line_count}")
    print(f"    - Logs parsed and sent: {parsed_count}")
    print(f"    - Lines skipped: {skipped_count}")
    print("="*30)