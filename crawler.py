import asyncio
import json
import os
import signal
import threading
from asyncio import Queue
from time import sleep

from database import Database
from document import Document
from servicebus import ScrapeMessageReceiver
from utility import wait_unless_cancelled

PAGE_RANK_PER_ITERATIONS = 10

class qObject:
    def __init__(self, docId: str, direction: str, depth: int, title=None):
        self.docId = docId
        self.title = title 
        self.direction = direction
        self.depth = depth

class ScrapeQueueItem:
    def __init__(self, initialDocId: str, depth: int, sbMessageId: str, sbReplyTo: str):
        self.docQueue = Queue()
        self.docId = initialDocId
        self.depth = depth
        self.sbMessageId = sbMessageId
        self.sbReplyTo = sbReplyTo

        upQ = qObject(initialDocId, 'up', 0)
        downQ = qObject(initialDocId, 'down', 0)
        self.docQueue.put_nowait(upQ)
        self.docQueue.put_nowait(downQ)

async def run_queue(db: Database, queue: Queue, cancel_event: asyncio.Event):
    smr = ScrapeMessageReceiver()

    def on_receive_message(msg_id, msg_content):
        print('here')
        msg_json = json.loads(msg_content)
        if type(msg_json) is dict:
            docId = msg_json['documentId']
            depth = msg_json['depth']
            replyTo = msg_json['replyTo']
            if docId and depth:
                newQueueItem = ScrapeQueueItem(docId, depth, msg_id, replyTo)
                print('queueing new document', docId, depth)
                queue.put_nowait(newQueueItem)
                return
        # else, we received an invalid message.
        print('received invalid message. ignoring.')

    receive_task = asyncio.create_task(smr.receive_loop(on_receive_message, cancel_event))

    iterations = 1
    while not cancel_event.is_set():
        try:
            currQueueItem: ScrapeQueueItem = await wait_unless_cancelled(queue.get(), cancel_event)
        except asyncio.CancelledError:
            break
        
        while not currQueueItem.docQueue.empty():
            curr_qObj: qObject = await currQueueItem.docQueue.get()
            
            shouldGetRefs = curr_qObj.direction == 'down'
            shouldGetCites = curr_qObj.direction == 'up'

            if curr_qObj.depth >= currQueueItem.depth:
                print('skipping', curr_qObj.docId, currQueueItem.docQueue.qsize())
                continue

            newDepth = curr_qObj.depth + 1

            if db.doc_is_visited(curr_qObj.docId):
                if shouldGetRefs:
                    for ref in db.get_references(curr_qObj.docId):
                        refQObj = qObject(ref, 'down', newDepth)
                        currQueueItem.docQueue.put_nowait(refQObj)
                if shouldGetCites:
                    for cite in db.get_references(curr_qObj.docId):
                        citeQObj = qObject(cite, 'up', newDepth)
                        currQueueItem.docQueue.put_nowait(citeQObj)
            else:
                doc = Document(id=curr_qObj.docId, citeBool=shouldGetCites, refBool=shouldGetRefs)
                db.insert_document(doc)
                iterations = (iterations + 1) % PAGE_RANK_PER_ITERATIONS
                if iterations == 0:
                    db.call_page_rank()
                    db.compute_author_popularity()
                
                for ref in db.get_references(curr_qObj.docId):
                    refQObj = qObject(ref, 'down', newDepth)
                    currQueueItem.docQueue.put_nowait(refQObj)
                for cite in db.get_references(curr_qObj.docId):
                    citeQObj = qObject(cite, 'up', newDepth)
                    currQueueItem.docQueue.put_nowait(citeQObj)
            
            print('finished', curr_qObj.docId, currQueueItem.docQueue.qsize())
        
        # when a queue finishes, send a message signalling completion
        if currQueueItem.sbMessageId:
            await smr.send_response(currQueueItem.sbMessageId, currQueueItem.sbReplyTo, currQueueItem.docId)
        print('finished scraping document', currQueueItem.docId)
    
    # await receive when loop is cancelled
    await receive_task

async def main():
    # These are set using environment variables

    user = os.environ['NEO4J_USER']
    password = os.environ['NEO4J_PASSWORD']
    uri = os.environ['NEO4J_URI']

    db = Database(user=user, password=password, uri=uri)
    scrapeQueue = Queue()
    cancelEvent = asyncio.Event()

    # handle interrupt signal
    def signal_handler(signum, frame):
        cancelEvent.set()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # for testing
    # testId = '12229'
    # testQueueItem = ScrapeQueueItem(testId, 3, '')
    # scrapeQueue.put_nowait(testQueueItem)

    print('ready')

    await run_queue(db, scrapeQueue, cancelEvent)
    print('shutting down.')

if __name__ == "__main__":
    asyncio.run(main())
