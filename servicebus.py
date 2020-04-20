import asyncio
import os
import signal
import sys
import threading

from azure.servicebus.aio import Message, QueueClient, ServiceBusClient
from azure.servicebus.common.constants import ReceiveSettleMode

SCRAPE_QUEUE_NAME = 'scrape'

class ScrapeMessageReceiver:
    def __init__(self):
        self.connection_string = os.environ['SB_CONNECTION_STRING']
        self._scrape_client = QueueClient.from_connection_string(self.connection_string, SCRAPE_QUEUE_NAME)
    
    async def receive_loop(self, on_scrape, cancel_event):
        async with self._scrape_client.get_receiver(mode=ReceiveSettleMode.ReceiveAndDelete) as messages:
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
                
                message: Message = await next_task
                message_id = message.properties.message_id
                msg_content = str(message)
                try:
                    on_scrape(message_id, msg_content)
                except:
                    print('Unexpected error:', sys.exc_info()[1])
    
    async def send_response(self, original_message_id: str, reply_to: str, reply_content: str):
        complete_client = QueueClient.from_connection_string(self.connection_string, reply_to)
        async with complete_client.get_sender() as reply_sender:
            reply_msg = Message(reply_content)
            reply_msg.properties.correlation_id = original_message_id
            await reply_sender.send(reply_msg)
