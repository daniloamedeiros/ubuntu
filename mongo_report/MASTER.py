from pymongo import MongoClient
import ssl

user = "teste"
passwd = "123123123"
url = "gplay-bphh6.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE"

conn_string = "mongodb+srv://%s:%s@%s" % (user, passwd, url)

print(conn_string)

client = MongoClient(conn_string)

dba = client['mongodba']

print(dba.list_collection_names())

relatorio = dba['relatorio_python']

collection = relatorio.find({}).count()

features = {'no_feat':0}
scenarios = {'no_scenario':0}
steps = {'no_steps':0}

for doc in collection:

    #print(doc)

    if 'Feature' in doc:
        feature = doc['Feature']

        if feature not in features:
            features[feature] = 1
        else:
            features[feature] += 1
    else:
        features['no_feat'] += 1

    if 'Scenario' in doc:
        scenario = doc['Scenario']

        if scenario not in scenarios:
            scenarios[scenario] = 1
        else:
            scenarios[scenario] += 1
    else:
        scenarios['no_scenario'] += 1
    
    if 'Step' in doc:
        step = doc['Step']

        status = "skipped"

        #print(doc['Step_status'])

        if 'Step_status' in doc:
            status = doc['Step_status']

        if step not in steps:
            steps[step] = {'tests':1, 'count':{status:1}}
        else:

            new_step = steps[step]
            
            new_test = new_step['tests'] + 1
            new_status_count = new_step['count']

            if status in new_status_count:
                print(new_status_count, status)
                new_status_count[status] += 1
            else:
                new_status_count[status] = 1
            
            steps[step] = {'tests':new_test, 'count':new_status_count}
    else:
        steps['no_steps'] += 1


print(collection.count())

print(features)
print(scenarios)
print(steps)