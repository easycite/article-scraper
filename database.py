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

    def doc_needs_scrape(self, docId):
        with self.driver.session() as session:
            query = '''
                MATCH (d:Document { id: $id })
                WHERE NOT EXISTS(d.publishYear) OR d.visited = false
                RETURN 1
            '''
            result = session.run(query, id=docId).single()
            return result is not None

    def doc_is_visited(self, docId):
        with self.driver.session() as session:
            existQuery = 'MATCH (d:Document { id: $id }) RETURN d.visited'
            result = session.run(existQuery, id=docId).single()
            return result is not None and result['d.visited'] == True
    
    def get_references(self, docId):
        with self.driver.session() as session:
            refQuery = '''
                MATCH (d:Document { id: $id })-[:CITES]->(ref:Document)
                WHERE ref.visited = false OR NOT EXISTS(ref.publishYear)
                RETURN ref.id
            '''
            results = session.run(refQuery, id=docId).records()
            refs = []
            for result in results:
                refs.append(result['ref.id'])
            return refs

    def get_citations(self, docId):
        with self.driver.session() as session:
            refQuery = '''
                MATCH (d:Document { id: $id })<-[:CITES]-(ref:Document)
                WHERE ref.visited = false OR NOT EXISTS(ref.publishYear)
                RETURN ref.id
            '''
            results = session.run(refQuery, id=docId).records()
            refs = []
            for result in results:
                refs.append(result['ref.id'])
            return refs
    
    def call_page_rank(self):
        with self.driver.session() as session:
            query = "CALL algo.pageRank('Document', 'CITES', { iterations: 20, dampingFactory: 0.85, write: true, writeProperty: 'pageRank' })"
            session.run(query)
    
    def compute_author_popularity(self):
        with self.driver.session() as session:
            query = '''
                MATCH (a:Author)-[:AUTHORED]->(d:Document)
                WITH a, sum(d.pageRank) as popularity
                SET a.popularity = popularity
            '''
            session.run(query)

    def insert_document(self, doc):
        if not doc:
            raise ValueError('A document is required.')
            
        with self.driver.session() as session:
            # create the document if it doesn't already exist
            docQuery = '''
                MERGE (d:Document { id: $id })
                SET d.title = $title,
                    d.abstract = $abstract,
                    d.publishYear = $publishYear,
                    d.publishDateStr = $publishDateStr,
                    d.publicationTitle = $publicationTitle,
                    d.visited = true
            '''
            session.run(docQuery, id=doc.id, title=doc.title, abstract=doc.abstract, publishYear=doc.publishYear, publishDateStr=doc.publishDateStr, publicationTitle=doc.publicationTitle)
            
            for author in doc.authors:
                authorQuery = '''
                    MATCH (d:Document { id: $id })
                    MERGE (a:Author { name: $name })
                    ON CREATE SET a.firstName = $firstName,
                        a.lastName = $lastName,
                        a.popularity = 0.0
                    MERGE (a)-[:AUTHORED]->(d)
                '''
                session.run(authorQuery, id=doc.id, name=author['name'], firstName=author['firstName'], lastName=author['lastName'])
            
            for kwd in doc.keywords:
                kwdQuery = '''
                    MATCH (d:Document { id: $id })
                    MERGE (k:Keyword { keyword: $kwd })
                    MERGE (d)-[:TAGGED_BY]->(k)
                '''
                session.run(kwdQuery, id=doc.id, kwd=kwd)

            for ref in doc.references:
                refQuery = '''
                    MATCH (d:Document { id: $id })
                    MERGE (ref:Document { id: $ref })
                    ON CREATE SET ref.visited = false
                    MERGE (d)-[:CITES]->(ref)
                '''
                session.run(refQuery, id=doc.id, ref=ref)

            for citation in doc.citations:
                citationQuery = '''
                    MATCH (d:Document { id: $id })
                    MERGE (citation:Document { id: $citation })
                    ON CREATE SET citation.visited = false
                    MERGE (citation)-[:CITES]->(d)
                '''
                session.run(citationQuery, id=doc.id, citation=citation)
