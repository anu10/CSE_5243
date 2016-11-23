from bs4 import BeautifulSoup
import os
import glob
import json
from nltk.corpus import stopwords
import preprocessing_config

# this function takes all .sgm files and it takes the reuter tag whose topic label is not empty, extract body, place, title and topic and store it in json format in parsed_documents_with_topics.txt file. 
def remove_empty_topics():
    result = []
    for infile in glob.glob(os.path.join(preprocessing_config.input_data_dir, "*.sgm")):
        print "Processing %s" %infile
        f = open(infile,'r')
        soup = BeautifulSoup(f, 'html.parser')
        soup.prettify()

        title = None
        topics = []
        places = []
        body = None
        data = {}
        for reuters in soup.find_all('reuters'):
            title = None
            del topics[:]
            del places[:]
            body = None
            data.clear()
            if reuters.title != None:
                title = reuters.title.string
                data["title"] = title
            if reuters.topics != None:
                for topic in reuters.topics.find_all('d'):
                    if topic.string != "":
                        topics.append(topic.string)
                        data["topics"] = list(topics)
            if reuters.places != None:
                for place in reuters.places.find_all('d'):
                    places.append(place.string)
                    data["places"] = list(places)
            if reuters.body != None:
                body = reuters.body.string.replace('\n', ' ')
                data["body"] = body

            if len(topics) != 0:
                result.append(data.copy())

        myfile = open(os.path.join(
                        preprocessing_config.output_data_dir, "parsed_documents_with_topics.txt"),
                        "w"
                    )
        json.dump(result, myfile, indent=4, separators=(',', ':'))
        myfile.close()
        return result

# this function takes parsed_documents_with_topics.txt file, for each reuter tag, it will extract out topic and body, split the body with spaces,remove duplicates, removes stopwords from body, places all keywords of body and topc labels into a list per reuter tag. It writes the list into parsed_documents_with_topics_output.txt file. 
def convert_to_transaction(parsed_documents_with_topics):
    apriori_format_data = []
    list_body = []
    topics_labels = []
    s = set()
    
    with open(os.path.join(
                        preprocessing_config.output_data_dir, "parsed_documents_with_topics_output.txt"), 'w') as f:
        for data_element in parsed_documents_with_topics:
            try:
                list_body = []
                topics_labels = []
                apriori_format_data = []
                document_string = ""
                if 'body' in data_element.keys():
                    document_string += data_element['body']
                    
                    
                if 'topics' in data_element.keys():
                    topics_labels.append(",".join(data_element['topics']))
                else:
                    topics_labels.append("")
                    
                list_body = document_string.split()
                s = set(list_body)
                list_body = list(s)
                filtered_words = [word for word in list_body if word not in stopwords.words('english')]
                apriori_format_data = filtered_words + topics_labels
                
                f.write(str(apriori_format_data))
                f.write('\n')
                
                #documents_as_string.append(document_string)
    
            except Exception as e:
                print(e)
    

def main():
    with open('data/output/parsed_documents_with_topics.txt') as f:
        parsed_documents_with_topics = json.load(f)
    convert_to_transaction(parsed_documents_with_topics)
    
main()