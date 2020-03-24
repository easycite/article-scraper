import requests 
import json

def get_refs_by_direct_link(doc_link):
    '''
    !!!!better to use get_refs_by_doc_id()
    
    Given the direct ieee link to a document as a string,
        makes an http GET request to IEEE
        recieves a json of the document's references

        write now rights json to a file, but will likely change
        
        Link must have the document id as the last parameter in the link 
        #ex: doc_link = 'https://ieeexplore.ieee.org/document/8862080'
            8862080 is the document id
    '''
    linkParts = doc_link.split('/')
    
    RefsLink = doc_link + '/references'
    GetLink = 'https://ieeexplore.ieee.org/rest/document/' + linkParts[-1] + '/references'
    Headers={'Referer':RefsLink + '#references'}
    refReq = requests.get(GetLink, headers=Headers)
    return json.loads(refReq.text)
 
def get_refs_by_doc_id(doc_id=''):
    '''
    Given a document id returns a dictionary of that document's references
    '''

    RefsLink = 'https://ieeexplore.ieee.org/document/' + doc_id + '/references'
    GetLink = 'https://ieeexplore.ieee.org/rest/document/' + doc_id + '/references'
    Headers={'Referer':RefsLink + '#references'}
    refReq = requests.get(GetLink, headers=Headers)
    return json.loads(refReq.text)

def search_by_doc_name(doc_name=''):
    '''
    Given a document name will return a dictionary of the search results
    '''
    doc_ref = doc_name.split()
    
    Referer = 'https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText='
    for w in doc_ref:
        Referer += '%'+w

    headers = {
        'Content-Type': 'application/json',
        'Referer':Referer
    }

    data = '{"queryText":"' + doc_name + '","returnFacets":["ALL"]}'

    response = requests.post('https://ieeexplore.ieee.org/rest/search', headers=headers, data=data)
    
    responseDict = json.loads(response.text)
    return responseDict

# print(direct_link_scrape('https://ieeexplore.ieee.org/document/4810674'))
# print(search_by_doc_name('Statistical Machine Learning in Natural Language Understanding: Object Constraint Language Translator for Business Process'))
# print(search_by_doc_id('4810674'))