from neo4j import GraphDatabase

class Database:

    def __init__(self, user, password, uri):   
        '''
        It is highly recommended to use environment variables
        when initialing 
        '''

        self.user = user
        self.password = password
        self.uri = uri
        self.driver = GraphDatabase.driver(uri, auth=(user,password))


    def insert_document(self, docId=None, title=None, docReferences=[]):

        if not docId and not title:
            print('A document id and/or title must be provided.')
            return None

        with self.driver.session() as session:
            print(f'Here are the refs:{docReferences} ')

            if docId and title:
                idQuery = "MATCH (d:Document {id:'" + docId + "'}) RETURN d"
                titleQuery = "MATCH (d:Document {title:'"+ title+"'}) RETURN d"

                idResult = session.run(idQuery)
                titleResult = session.run(titleQuery)

                if idResult.peek() and titleResult.peek():
                    for ref in docReferences:
                        query = "MERGE (d:Document {id:'"+ docId +"', title: '"+ title +" '}) MERGE (ref: Document {id:'"+ ref +"'}) MERGE (d)-[c:CITES]->(ref) RETURN d, ref, c "
                        results = session.run(query)
                elif idResult.peek() and not titleResult.peek():
                    docQuery = "MERGE (d:Document {id:'" + docId + "'}) SET d.title = '"+ title +"' RETURN d"
                    docResult = session.run(docQuery)
                    for ref in docReferences:
                        idQuery = "MATCH (d:Document {id:'" + docId + "'}) MERGE (ref: Document {id:'"+ ref +"'}) MERGE (d)-[c:CITES]->(ref) RETURN d, ref, c "
                        idResult = session.run(idQuery)                    
    
                elif not idResult.peek() and titleResult.peek():
                    docQuery = "MATCH (d:Document {title:'" + title + "'}) SET d.id = '" + docId + "' RETURN d"
                    docResult = session.run(docQuery)
                    for ref in docReferences:
                        print(ref)
                        titleQuery = "MATCH (d:Document {id:'" + title + "'}) MERGE (ref: Document {id:'"+ ref +"'}) MERGE (d)-[:CITES]->(ref) RETURN d, ref, c"
                        titleResult = session.run(idQuery)
                        print(titleResult.value())

                else:
                    print('Here')
                    docQuery = "CREATE (d:Document {title: '"+ title +"', id: '" + docId + "'} )"
                    docResults  = session.run(docQuery)
                    print(docResults)
                    for ref in docReferences:
                        query = "MATCH (d:Document { title: '"+ title +"', id:'" + docId + "'}) MERGE (ref: Document {id:'"+ ref +"'}) MERGE (d)-[c:CITES]->(ref) RETURN d, ref, c "                  
                        results = session.run(query)

            elif docId:
                docQuery = "MERGE (d:Document {id:'" + docId + "'}) RETURN d"
                docResult = session.run(docQuery)
                for ref in docReferences:
                    idQuery = "MATCH (d:Document {id:'" + docId + "'}) MERGE (ref: Document {id:'"+ ref +"'}) MERGE (d)-[c:CITES]->(ref) RETURN d, ref, c "
                    idResult = session.run(idQuery)

            elif title:
                docQuery = "MERGE (d:Document {title:'" + title + "'}) RETURN d"
                docResult = session.run(docQuery)
                for ref in docReferences:
                    titleQuery = "MATCH (d:Document {title:'" + title + "'}) MERGE (ref: Document {id:'"+ ref +"'}) MERGE (d)-[c:CITES]->(ref) RETURN d, ref, c"
                    titleResult = session.run(titleQuery)

        
