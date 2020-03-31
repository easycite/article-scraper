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


    def insert_document(self, docId=None, title=None, docReferences=[], docCitations=[], authors = []):

        if not docId and not title:
            print('A document id and/or title must be provided.')
            
        else:
            with self.driver.session() as session:
                # print(f'Here are the refs:{docReferences} ')

                if docId and title:
                    # This will work assuming that no document in database exists with a title but no id
                    # In theory, this should be true always

                    idQuery = "MERGE (d:Document {id:'" + docId + "'}) ON CREATE SET d.title = '"+ title +"' RETURN d"
                    idResult = session.run(idQuery)

                    for ref in docReferences:
                        query = "MATCH (d:Document {id:'"+ docId +"', title: '"+ title +" '}) MERGE (ref: Document {id:'"+ ref +"'}) MERGE (d)-[c:CITES]->(ref) RETURN d, ref, c "
                        results = session.run(query)
                    for citation in docCitations:
                        citationQuery = "MERGE (citation:Document {id: '"+ citation +"' })  MATCH (d:Document {id: '"+docId+"', title: '" + title + "'}) MERGE (citation)-[c:CITES]->(d) RETURN citaion, d, c"
                        citationResult = session.run(citationQuery)
                        
                elif docId:
                    docQuery = "MERGE (d:Document {id:'" + docId + "'}) RETURN d"
                    docResult = session.run(docQuery)
                    for ref in docReferences:
                        idQuery = "MATCH (d:Document {id:'" + docId + "'}) MERGE (ref: Document {id:'"+ ref +"'}) MERGE (d)-[c:CITES]->(ref) RETURN d, ref, c "
                        idResult = session.run(idQuery)

                    for citation in docCitations:
                        citationQuery = "MERGE (citation:Document {id: '"+ citation +"' })  MATCH (d:Document {id: '"+docId+"'}) MERGE (citation)-[c:CITES]->(d) RETURN citation, d, c"
                        citationResult = session.run(citationQuery)
                    

                elif title:
                    # In theory this should never be called. A document with a title will never be inserted without an id
                    docQuery = "MERGE (d:Document {title:'" + title + "'}) RETURN d"
                    docResult = session.run(docQuery)
                    for ref in docReferences:
                        titleQuery = "MATCH (d:Document {title:'" + title + "'}) MERGE (ref: Document {id:'"+ ref +"'}) MERGE (d)-[c:CITES]->(ref) RETURN d, ref, c"
                        titleResult = session.run(titleQuery)
                    for citation in docCitations:
                        citationQuery = "MERGE (citation:Document {id: '"+ citation +"' })  MATCH (d:Document {title: '"+ title +"'}) MERGE (citation)-[c:CITES]->(d) RETURN citation, d, c"
                        citationResult = session.run(citationQuery)

                for author in authors:
                    # print(author)
                    authorQuery = "MATCH (d:Document {id:'"+ docId +"'}) MERGE (a:Author {name:'"+author+"'}) MERGE (a)-[:AUTHORED]->(d) RETURN a,d"
                    authorResult= session.run(authorQuery)
                    # print(authorResult)



    
