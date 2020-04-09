import os
import sys
import signal
import asyncio
from azure.servicebus.aio import ServiceBusClient, Message, QueueClient
import threading

SCRAPE_QUEUE_NAME = 'scrape'
COMPLETE_QUEUE_NAME = 'scrape-complete'

class ScrapeMessageReceiver:
    def __init__(self):
        connection_string = os.environ['SB_CONNECTION_STRING']
        self._scrape_client = QueueClient.from_connection_string(connection_string, SCRAPE_QUEUE_NAME)
        self._complete_client = QueueClient.from_connection_string(connection_string, COMPLETE_QUEUE_NAME)
    
    async def receive_loop(self, on_scrape, cancel_event):
        async with self._scrape_client.get_receiver() as messages:
            while True:
                next_task = asyncio.create_task(messages.__anext__())
                
                done, _ = await asyncio.wait({ next_task, cancel_event.wait() }, return_when=asyncio.FIRST_COMPLETED)
                if not next_task in done:
                    next_task.cancel()
                    try:
                        await next_task
                    except:
                        pass
                    return
                
                message = await next_task
                msg_content = str(message)
                on_scrape(msg_content)
                async with self._complete_client.get_sender() as reply_sender:
                    reply_msg = Message(msg_content)
                    reply_msg.properties.correlation_id = message.properties.message_id
                    await reply_sender.send(reply_msg)
                await message.complete()

async def _test():
    print('testing service bus receive loop.')

    cancel_event = asyncio.Event()

    def signal_handler(signum, frame):
        cancel_event.set()
    
    signal.signal(signal.SIGINT, signal_handler)

    receiver = ScrapeMessageReceiver()
    await receiver.receive_loop(lambda message: print(message), cancel_event)

if __name__ == '__main__':
    asyncio.run(_test())
