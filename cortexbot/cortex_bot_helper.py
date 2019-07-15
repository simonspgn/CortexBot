#!/usr/bin/python3.6

# Cortex Bot Helper for Mattermost Integration
# Simon Spangenberg
# 20/06/2019

import sys
import os
import time
from cortex_bot import Job
from cortex_bot import Run
from cortex_bot import Analyzer
from cortex_bot import Cortex

run_object = Run()
cortex_object = Cortex()
incoming_WH_link = "<MATTERMOST_INCOMING_WEBHOOK_URL>"

# Method to manage multiple jobs
def multiple_run(analyzers_ls, dataType, data, tlp, forceFlag, query_user):
    # Initialize the response and counters
    response = ""
    num_job = 0
    part = 1
    # Start running every analyzer in the list
    for analyzer in analyzers_ls:
        num_job+=1
        # Mattermost outputs are limited. Thus, we send a response for every 15 jobs ran.
        if num_job > 15:
            returnParts(response,part,query_user)
            # Update the response and counters after returning a part of the response
            part+=1
            response = ""
            num_job = 0
        job = cortex_object.runByName(analyzer.name,dataType,data,tlp,forceFlag)
        response += single_run(job)
    # End of job, case we have less than 15 jobs.
    if part == 1:
        returnParts(response,0, query_user)
    else:
         # In case there are more than 15 jobs, return the remaining ones
        returnParts(response,part, query_user)

# Method to run a single job
def single_run(job):
    response = run_object.formatRunResponse(job)
    return response

# Method to format and return the output to mattermost;
def returnParts(response,part, query_user):
    if part == 0:
        response= "# Hi "+ query_user +", here is a Summary of the job(s) you ran!\n\n---\n\n" + response
    else:
        response= "# Hi "+ query_user +", here is a Summary of all the jobs you ran: Part {}\n\n---\n\n".format(part) + response
    # Curl to Mattermost Server using the incoming webhhook configured.
    command = "curl -k -i -X POST -H \'Content-Type: application/json\' -d \'{\"channel\":\"@"+query_user+"\",\"text\":\""+response+"\"}\' "+ incoming_WH_link
    os.system(command)

def main():
    # Get the arguments
    args_ls = sys.argv
    # Instantiote all the required arguments
    analyzer_name = args_ls[1]
    dataType = args_ls[2]
    data = args_ls[3]
    tlp = int(args_ls[4])
    forceFlag = int(args_ls[5])
    query_user = args_ls[6]
    # Process the query.
    try:
        if analyzer_name=="multiple":
            analyzers_ls = cortex_object.analyzerType(dataType)
            multiple_run(analyzers_ls, dataType, data, tlp, forceFlag, query_user)
        else:
            job = cortex_object.runByName(analyzer_name,dataType,data,tlp,forceFlag)
            response = single_run(job)
            returnParts(response,0, query_user)
    except:
        returnParts("Something went wrong in your query, please try to run the job separately",0, query_user)
    return

if __name__ == "__main__":
    main()
