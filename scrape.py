import requests 

def direct_link_scrape(doc_link):
    '''
    Given the direct ieee link to a document as a string,
        makes an http GET request to IEEE
        recieves a json of the document's references

        write now rights json to a file, but will likely change
    '''
    #ex: doc_link = 'https://ieeexplore.ieee.org/document/8862080'
    docRefs = doc_link + '/references'
    headers={'Referer':docRefs + '#references'}
    r = requests.get(docRefs, headers=headers)
    f = open('test.json','w')
    #look into r.json()
    f.write(r.text)
    f.close()