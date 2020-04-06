import os
import re
import json
from datetime import datetime
import config
import glob
import io

def parse_logs_json(filename):

    # lendo json
    json_file_ptr = open(filename, 'r')
    json_text = json_file_ptr.read()
    json_file_ptr.close()
    json_format = json.loads(json_text)

    # escrevendo tudo em um arquivo
    output_string = ""

    for feature in json_format: 
        scenarios = feature['elements']
        output_string += (feature['keyword'] + " " + feature['name'] + " --- " + feature['status'] + "\n\n")
        
        for scenario in scenarios:
            output_string += ("\t" + scenario['keyword'] + " " + scenario['name'] + " --- " + scenario['status'] + "\n\n")

            for step in scenario['steps']:
                
                if 'result' in step:
                    output_string += ("\t\t" + step['keyword'] + " " + step['name'] + " --- " + step['result']['status'] +\
                                    " " + str(step['result']['duration']) + "\n\n")
                else:
                    output_string += ("\t\t" + step['keyword'] + " " + step['name'] + " --- " + "skipped" + "\n\n")
        output_string += ("\n\n")
    return output_string
