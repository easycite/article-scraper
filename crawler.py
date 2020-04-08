from database import Database
from document import Document
import os
from queue import Queue
from time import sleep
import threading

class qObject:
    def __init__(self, docId, direction, depth, title=None):
        self.docId = docId
        self.title = title 
        self.direction = direction
        self.depth = depth

def thread_function(db: Database, queue):
    # lock function
    # pop from queue
    # insert to database
    # 
    maxDepth = 3
    iterations = 1
    pageRankPerIter = 10
    while True:
        curr_qObj = queue.get()
        print('started', curr_qObj.docId)

        # print(curr_qObj)
        docId = curr_qObj.docId
        docTitle = curr_qObj.title
        direction = curr_qObj.direction
        depth =curr_qObj.depth

        refBool = True
        citeBool = True

        if direction == 'down':
            citeBool = False 
        elif direction == 'up':
            refBool = False
        
        if depth >= maxDepth:
            print('skipping', curr_qObj.docId, queue.qsize())
            continue

        newDepth = depth + 1

        if db.doc_is_visited(docId):
            for ref in db.get_references(docId):
                newQObj = qObject(docId=ref,direction='down',depth=newDepth)
                queue.put_nowait(newQObj)
            for cite in db.get_citations(docId):
                newQObj = qObject(docId=cite,direction='up',depth=newDepth)
                queue.put_nowait(newQObj)
        else:
            doc = Document(id=docId, title=docTitle, citeBool=citeBool, refBool=refBool)
            # try:
            #     doc = Document(id=docId, title=docTitle, citeBool=citeBool, refBool=refBool)
            # except:
            #     print('failed', curr_qObj.docId, queue.qsize())
            #     continue
            db.insert_document(doc)
            iterations = (iterations + 1) % pageRankPerIter
            if iterations == 0:
                db.call_page_rank()

            for ref in doc.references:                
                newQObj = qObject(docId=ref,direction='down',depth=newDepth)
                queue.put_nowait(newQObj)
            for cite in doc.citations:
                newQObj = qObject(docId=cite,direction='up',depth=newDepth)
                queue.put_nowait(newQObj)
        
        print('finished', curr_qObj.docId, queue.qsize())

if __name__ == "__main__":
    # These are set using environment variables

    user = os.environ['NEO4J_USER']
    password = os.environ['NEO4J_PASSWORD']
    uri = os.environ['NEO4J_URI']

    db = Database(user=user, password=password, uri=uri)

    refsQueue = Queue()

    # TESTING --------------------------------------------------------------
    testId = '12229'
    downQObj = qObject(docId=testId,direction='down',depth=0)
    upQObj = qObject(docId=testId,direction='up', depth=0)
    refsQueue.put(downQObj)
    refsQueue.put(upQObj)
    x = threading.Thread(target=thread_function, args=(db, refsQueue))
    x.start()
    x.join()
    # TESTING ---------------------------------------------------------------
