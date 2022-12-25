import threading
import functools

def run():
    events = []
    for request in requests:
        event = threading.Event()
        callback_with_event = functools.partial(callback, event)
        client.send_request(request, callback_with_event)
        events.append(event)

    return events

def callback(event, error, response):
    # handle response
    event.set()

def wait_for_events(events):
    for event in events:
        event.wait()

def main():
    events = run()
    wait_for_events(events)