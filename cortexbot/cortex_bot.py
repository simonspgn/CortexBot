#!/usr/bin/python3.6

# Cortex Bot for Mattermost Integration
# Simon Spangenberg
# 20/06/2019

import json
import cgi
from formats import *

# Change API and CORTEX API KEY
api = Api('<CORTEX_INSTANCE_URL>','<CORTEX_BOT_USER_API_KEY>')
# Link of the Cortex Instance
link = "<CORTEX_INSTANCE_URL>"
# Input the MATTERMOST TOKEN
token = "<MATTERMOST TOKEN>"
data_type_ls=["domain","ip","url","fqdn","uri_path","user-agent","hash","email","mail","mail_subject","registry","regexp","other","filename"]
# TLP Dictionnary, mapping tlp colors to numbers.
dict_tlp = {"white":0,"green":1,"amber":2,"red":3}

print("Content-type: application/json\r\n\r\n")

# Check validity of toke - security step for Mattermost.
def valid(query_token):
    if query_token == token:
        return True
    else:
        return False

# Analyzers Function
def analyzers(resp):
    # Initialize objects
    analyzer_object=Analyzer()
    cortex_object=Cortex(api)
    length=len(resp)
    # if all analyzers are searched (only one argument is given): /Cortex analyzers
    if length==1:
        analyzers_ls_all = cortex_object.allAnalyzers()
        if len(analyzers_ls_all) == 0:
            return ":speak_no_evil:No enabled analyzer found"
        # Else return all analyzers found
        else:
            return analyzer_object.printAllAnalyzers(analyzers_ls_all)
    # If a more specific search is required (more arguments given by the user).
    elif length==2:
        # Case 1: User wants to find analyzers allowing a specific data type
        second_arg = resp[1].lower()
        if second_arg in data_type_ls:
            analyzers_ls = cortex_object.analyzerType(second_arg)
            return analyzer_object.printDataTypeAnalyzers(second_arg, analyzers_ls)
        # Case 2: User wants to find a specific analyzer
        else:
            analyzer = cortex_object.analyzerName(resp[1])
            # If no analyzer was found, the user gave a wrong argument or the given analyzer is simply not enabled.
            if analyzer==None:
                return ":see_no_evil:No enabled analyzer found, check that your input is correct or type  `/cortex help`"
            # Analyzer found, return and display info
            else:
                return analyzer_object.printAnalyzerInformation(analyzer)
    # If more than two input arguments were given, return error message.
    else:
        return ":disappointed: Too many input arguments. Consult `/cortex help` for information"

# Jobs function
def jobs(resp):
    # Initialize objects
    job_object=Job(api,link)
    analyzer_object = Analyzer()
    cortex_object = Cortex(api)
    length = len(resp)
    # Initiate a list of all existing jobs
    jobs_ls_all = cortex_object.allJobs()
    # Initiate a list of the last 10 existing jobs.
    jobs_ls = cortex_object.limitedJobs()
    # Get a list of all enabled analyzers
    analyzers_all_ls = cortex_object.allAnalyzers()
    # get a list of only the enabled analyzer's names
    analyzers_ls = analyzer_object.filterAnalyzers(analyzers_all_ls)
    # If all the jobs are searched (only one input argument is given)
    if length==1:
        # If no jobs are found, display message and return
        if len(jobs_ls_all)==0:
            return ":hear_no_evil: No existing job found"
        # Existing jobs were found
        else:
            return job_object.formatAllJobs(jobs_ls,jobs_ls_all)
    # If a more specific search is required (more arguments given by the user). The search will be divided in three different cases depending on the arguments given by the user; We have here three different possibilities of search: by a$
    elif length==2:
        # We want the input to be case insensitive (note: this is not valid for job IDs or Analyzer Names)
        second_arg = resp[1].lower()
        # First case: job search by analyzer name
        if resp[1] in analyzers_ls:
            return job_object.formatJobAnalyzerName(resp[1],jobs_ls_all)
        # Second case: job search by data type
        elif second_arg in data_type_ls:
            return job_object.formatJobDataTypes(second_arg, jobs_ls_all)
        # Third case: Job search by ID.
        else:
            # Check that the given ID corresponds to an existing job. Else, output and exception and return error message
            try:
                job = cortex_object.jobId(resp[1])
                # Create the response
                response = job_object.formatJobId(job) + job_object.addStartDate(job)
            except:
                response=":sweat_smile: Could not fetch Job from given ID or analyzer name. Please ensure the information is correct or check `/cortex help`"
            return response
    # If 3 input arguments are given, the user requests more specific information concerning a given job: Report or Artifacts
    elif length==3:
        second_arg = resp[1].lower()
        # User is looking for report
        if second_arg=="report":
            # Get the report and print out the taxonomy/summary.
            try:
                job = cortex_object.jobId(resp[2])
                # The report will depend on the job's status.
                if job.status == "Success":
                    response = job_object.formatSuccessfulJobReport(job)
                elif job.status == "Failure":
                    response = job_object.formatFailedJobReport(job)
                else:
                    response = ":clock10: The Job is still in progress. Please check back when it is completed\n"
            except:
                response=":unamused: Could not fetch Report from given Job ID. Please ensure the information is correct or check `/cortex help`."
            return response
        # User is looking for artifacts
        elif second_arg=="artifacts":
            # Try to find artifacts, if no artifacts are found, display message and return
            artifact = cortex_object.jobArtifacts(resp[2])
            if artifact==[]:
                response=":scream: No artifact found, please check the job ID you have entered or consult `/cortex help`"
                return response
            # This case has purposedly been left blank. At this point, it is unknown the format that artifacts have. Change it if needed.
            else:
                return "Still under construction\n"
        else:
            return ":no_good: Invalid input arguments, please check `/cortex help` for more information"
    # If more than three arguments were given, return and display error message.
    else:
        return ":poop: Too many input arguments. consult `/cortex help` for information"

def run(resp, query_user):
    # Initialize all objects.
    job_object=Job(api,link)
    analyzer_object = Analyzer()
    run_object = Run(api,link)
    cortex_object = Cortex(api)
    length=len(resp)
    # Intialize a list of all enabled analyzers
    analyzers_ls = analyzer_object.filterAnalyzers(cortex_object.allAnalyzers())
    # Set the force flag
    resp, flag = run_object.forceFlag(resp)
    # Check first argument corresponds to a valid enabled analyzer.
    if resp[1] in analyzers_ls and length<=5:
        analyzer_name = resp[1]
        try:
            # Check if all the arguments given are valid.
            if type(run_object.getArgs(resp))==str:
                return run_object.getArgs(resp)
            # If they are valid, set the arguments variables.
            else:
                (data_type_query,data,tlp)=run_object.getArgs(resp)
            # Run analyzer - To run the analyzer, a subprocess will be created by calling cortex_bot_helper.py
            args_ls = ["python3.6","cortex_bot_helper.py",analyzer_name,data_type_query,data,str(tlp),str(flag),query_user]
            return run_object.callSubProcess(args_ls)
        except:
            return ":pig: Oops, something went wrong. You probably don't have enough arguments or something is wrong in your data type or in your data arguments. Check `/cortex help run` for more details\n"
    # Here we run all available analyzers.
    elif resp[1] == "*" and length<=5:
        try:
            # Check if all the arguments given are valid.
            if type(run_object.getArgs(resp))==str:
                return run_object.getArgs(resp)
            # If they are valid, set the arguments variables.
            else:
                (data_type_query,data,tlp)=run_object.getArgs(resp)
            args_ls = ["python3.6","cortex_bot_helper.py","multiple",data_type_query,data,str(tlp),str(flag),query_user]
            return run_object.callSubProcess(args_ls)
        except:
            return ":pig: Oops, something went wrong. You probably don't have enough arguments or something is wrong in your data type or in your data arguments. Check `/cortex help run` for more details\n"
    else:
        return ":construction: Could not run the job. Please ensure that you have correctly input the neccesary information. Check `/cortex help run` for more details\n"


def main():
    help_object = Help()
    # Initiate/get the HTTP GET request parameters
    form = cgi.FieldStorage()
    # Check token validity. If not valid, return
    query_token = form.getvalue('token')
    # Get the Mattermost query user name
    query_user = form.getvalue('user_name')
    if not valid(query_token):
        return json.dumps({"response_type":"in_channel","text":":skull: WARNING: attempt to connect to Cortex server with wrong token! Is someone trying to hack into Cortex :warning:"})
    else:
        # get the commands requested by the user in mattermost.
        query_text = form.getvalue('text')
        # Check input arguments have been given, else print error message
        if query_text == None:
            return json.dumps({"response_type":"ephemeral","text":":raising_hand: Invalid usage of the `/cortex` command. Please type `/cortex help` for more information"})
        else:
            resp = query_text.split()
            # Check if the *all* tag is given in arguments:
            if resp[-1]=="all":
                response_type="in_channel"
                resp=resp[:-1]
            else:
                response_type="ephemeral"
        # start processing arguments, if invalid argument given, return error message.
        first_arg = resp[0].lower()
        if first_arg=="analyzers":
            response = analyzers(resp)
        elif first_arg=="jobs":
            response = jobs(resp)
        elif first_arg=="run" and len(resp)>1:
            response = run(resp,query_user)
        elif first_arg=="help" and len(resp)==1:
            response = help_object.mainHelp(link)
        elif first_arg=="help" and resp[1].lower()=="run" and len(resp)==2:
            response = help_object.runHelp(link)
        else:
            response=":eyes: Invalid usage of the `/cortex` command. Please type `/cortex help` for more information or `/cortex help run` if you want to run a job"
    data = {"response_type":response_type,"text":response}
    json_data=json.dumps(data)
    return json_data

if __name__ == "__main__":
    print(main())
