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

def thread_function(db, queue):
    # lock function
    # pop from queue
    # insert to database
    # 
    maxDepth  = 10
    while True:
        curr_qObj = queue.get()
        print(curr_qObj.docId)

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

        if depth < maxDepth:
            doc = Document(id=docId, title=docTitle,citeBool=citeBool, refBool=refBool)
            authors = []
            for author in doc.authors:
                authName = ''
                if 'firstName' in author:
                    authName += author['firstName'] + ' '
                if 'lastName' in author:
                    authName+= author['lastName']
                authors.append(authName)

            db.insert_document(docId=docId, title=docTitle, docReferences= doc.references, docCitations = doc.citations, authors=authors)
            newDepth = depth + 1
            for ref in doc.references:                
                newQObj = qObject(docId=ref,direction='down',depth=newDepth)
                queue.put(newQObj)
            
            for cite in doc.citations:
                
                newQObj = qObject(docId=cite,direction='up',depth=newDepth)
                queue.put(newQObj)



            sleep(10)
    


def main():
    # These are set using environment variables

    user = os.environ['NEO4J_USER']
    password = os.environ['NEO4J_PASSWORD']
    uri = os.environ['NEO4J_URI']

    db = Database(user=user, password=password, uri=uri)

    refsQueue = Queue()

    # TESTING --------------------------------------------------------------
    testId = '8862080'
    qObj = qObject(docId=testId,direction='down',depth=0)
    refsQueue.put(qObj)
    x = threading.Thread(target=thread_function, args=(db, refsQueue))
    x.start()
    # TESTING ---------------------------------------------------------------

main()
