import queue
from fritzconnection.core.fritzmonitor import FritzMonitor
import requests

url = "http://127.0.0.1:8080/api/v1/call"


def process_events(monitor, event_queue, healthcheck_interval=10):
    while True:
        try:
            event = event_queue.get(timeout=healthcheck_interval)
        except queue.Empty:
            # check health:
            if not monitor.is_alive:
                raise OSError("Error: fritzmonitor connection failed")
        else:
            # do event processing here:
            print(event)
            process_event(event)


def process_event(event):
    event_split = event.split(";")
    date = event_split[0]
    event_type = event_split[1]
    number = ""
    if event_type == "RING":
        number = event_split[3]
    elif event_type == "CONNECT":
        number = event_split[4]

    if number != "":
        data = {
            "date": date,
            "eventType": event_type.lower(),
            "number": number
        }
        send_event(data)


def send_event(event_json):
    requests.post(url, json=event_json)


def main():
    """Entry point: example to use FritzMonitor.
    """
    try:
        # as a context manager FritzMonitor will shut down the monitor thread
        with FritzMonitor(address='192.168.178.1') as monitor:
            event_queue = monitor.start()
            process_events(monitor, event_queue)
    except (OSError, KeyboardInterrupt) as err:
        print(err)


if __name__ == "__main__":
    # process_event("10.11.22 22:39:38;CONNECT;1;12;0612345678;")
    main()
