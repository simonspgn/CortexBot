#!/usr/bin/python3.6

# Cortex Bot for Mattermost Integration
# Simon Spangenberg
# 20/06/2019

import json
import cgi, cgitb
import time
import subprocess
from cortex4py.api import Api
from cortex4py.query import *
from cortex4py.models import Organization

# Change API and TOKEN
api = Api("<CORTEX_INSTANCE_URL>","<CORTEX_USER_API_KEY>")
# Link of the Cortex Instance
link = "<CORTEX_INSTANCE_URL>"
# Input the MATTERMOST TOKEN
token = "<MATTERMOST TOKEN>"
data_type_ls=["domain","ip","url","fqdn","uri_path","user-agent","hash","email","mail","mail_subject","registry","regexp","other","filename"]
# So far, cortex can only be run through mattermost with the following 4 data types.
run_ls = ["domain","ip","url","hash"]
# TLP Dictionnary, mapping tlp colors to numbers.
dict_tlp = {"white":0,"green":1,"amber":2,"red":3}

print("Content-type: application/json\r\n\r\n")

# Cortex Class: Includes all the script's direct interactions with Cortex. Returns Lists, Jobs or Analyzers depending on Query.
class Cortex:

  # Method to get all enabled analyzers from Cortex
    def allAnalyzers(self):
        return api.analyzers.find_all({}, range='all')

    # Method to get all the analyzers that can run on a specific data type.
    def analyzerType(self,type):
        return api.analyzers.get_by_type(type)

    # Method to get an analyzer by name from Cortex
    def analyzerName(self,name):
        return api.analyzers.get_by_name(name)

    # Method to run an analyzer. Returns a job.
    def runByName(self,name,data_type,data,tlp,flag):
        return api.analyzers.run_by_name(name, {'data':data,'dataType':data_type,'tlp':tlp},force=flag)

    # Method to find all existing jobs from Cortex.
    def allJobs(self):
        return api.jobs.find_all({}, range='all')

    # Method to find the 10 most recent jobs from Cortex
    def limitedJobs(self):
        return api.jobs.find_all({}, range='0-10',sort='-createdAt')

    # Method to get a job's report from Cortex
    def jobReport(self,id):
        return api.jobs.get_report(id).report

    # Method to get a job by ID from Cortex.
    def jobId(self,id):
        return api.jobs.get_by_id(id)

    # Method to get a job's artifacts by ID from Cortex
    def jobArtifacts(self,id):
        return api.jobs.get_artifacts(id)


# Analyzer Class, contains methods belonging to analyzer types. Many of the methods in this class format the markdown response returned to Mattermost.
class Analyzer:

    # filter a list of analyzers to keep just their names
    def filterAnalyzers(self,analyzer_ls):
      return list(map(lambda x: x.name, analyzer_ls))

    # In case a search for all analyzers is conducted
    def printAllAnalyzers(self,analyzers_ls):
        response="There are a total of "+str(len(analyzers_ls))+" enabled analyzers\n\n"
        response+="|Status|Analyzers|\n|:------------||:-------------|\n"
        for analyzer in analyzers_ls:
            response +="|:heavy_check_mark:|"+ analyzer.name+"|\n"
        return response

    # In case a search for all analyzers allowed with a given data type is conducted.
    def printDataTypeAnalyzers(self,data_type, analyzers_ls):
        response=(str(len(analyzers_ls)))+" enabled analyzers found corresponding with data type "+data_type+"\n\n"
        response += "|Status|Analyzers|Data Types|\n|:------------||:-------------|:----------|\n"
        for analyzer in analyzers_ls:
            response +="|:heavy_check_mark:|"+ analyzer.name+"|"+', '.join(analyzer.dataTypeList)+"|\n"
        return response
    # In case a search for more information on a specific Analyzer is conducted.
    def printAnalyzerInformation(self,analyzer):
        # Note: Some of the analyzers features are not properly defined in analyze.py module.
        # Converting the analyzer model to json allows to get further infomation.
        analyzer_json=json.loads(str(analyzer))
        response="|Parameter|Value|\n|:------|:------|\n \
          |Name|"+analyzer.name+"|\n \
          |Base Config|"+analyzer.baseConfig+"|\n \
          |Description|"+analyzer.description+"|\n \
          |Data Types|"+', '.join(analyzer.dataTypeList)+"|\n \
          |ID|"+analyzer.id+"|\n \
          |Version|"+analyzer.version+"|\n \
          |Max TLP|" + str(analyzer_json['maxTlp']) +"|\n \
          |Max Pap|" + str(analyzer_json['maxPap']) +"|\n \
          |Author|"+analyzer.author+"|\n \
          |URL|"+analyzer.url+"|\n \
          |License|"+analyzer.license+"|\n \
          |Created By|"+analyzer.createdBy+"|\n \
          |Created At|"+str(analyzer_json['createdAt'])+"\n"
        return response

# Job Class, contains methods belonging to job types. Many of the methods in this class format the markdown response returned to Mattermost.
class Job:

    def __init__(self):
      self.cortex_object=Cortex()

    # Formatting purpose, returns emoji belonging to a job status
    def getJobStatus(self,job):
        if job.status=="Success":
            return ":heavy_check_mark: "
        elif job.status=="Failure":
            return ":x: "
        else:
            return ":heavy_minus_sign: "

    # Check the status of a job. If the job is completed, return True.
    def checkJobStatus(self, job):
        if job.status != "Success" and job.status != "Failure":
            return False
        else:
            return True

    # get the number of successful jobs within given list
    def getNumberSuccessfulJobs(self,jobs_ls):
        return len(list(filter(lambda x:x.status=="Success", jobs_ls)))

    # get the number of failed jobs within given list
    def getNumberFailedJobs(self,jobs_ls):
        return len(list(filter(lambda x:x.status=="Failure", jobs_ls)))

    # filter a list of jobs based on analyzer or data type
    def filterJobs(self,jobs_ls_all,flag, el):
        if flag==True:
          return list(filter(lambda x: x.analyzerName==el,jobs_ls_all))
        else:
          return list(filter(lambda x: x.dataType==el,jobs_ls_all))

    # generate a mark down formatted table with required information
    def generateMarkDownTable(self,jobs_ls):
        response="Here are the ten most recent Jobs\n\n"
        response+="|Status|Jobs ID|Analyzer Name|Data Type|Report|\n|:--------|:--------|:---------|:--------|:--------|\n"
        for job in jobs_ls:
            response+="|"+self.getJobStatus(job)+"|{}|{}|{}|{}|\n".format(job.id,job.analyzerName,job.dataType,"[**See Report**]("+link+"/index.html#!/jobs/"+job.id+")\n")
        response+="---\n"
        response+=":heavy_plus_sign: [**See all**]("+link+"/index.html#!/jobs/)\n\n"
        response+="---\n"
        return response

  # Simple Markdown Formatting print method if all jobs are asked for.
    def formatAllJobs(self,jobs_ls,jobs_ls_all):
        num_jobs = len(jobs_ls_all)
        response="There are a total of "+str(num_jobs)+" jobs found\n"
        # start response formatting (in Markdown)
        response+=str(self.getNumberSuccessfulJobs(jobs_ls_all))+" out of "+ str(num_jobs)+" are successful\n"
        response+=str(self.getNumberFailedJobs(jobs_ls_all))+" out of "+ str(num_jobs)+" are failures\n\n"
        # generate the main table and add it to the final response
        response+=self.generateMarkDownTable(jobs_ls)
        return response

    # Markdown fomatting method if jobs based on analyzer name are searched for.
    def formatJobAnalyzerName(self,analyzer_Name,jobs_ls_all):
        # Filter jobs based on given analyzer name.
        jobs_ls = self.filterJobs(jobs_ls_all,True,analyzer_Name)
        num_jobs = len(jobs_ls)
        # start response formatting (in Markdown)
        response="There are a total of "+str(num_jobs)+" jobs found for the analyzer: **"+analyzer_Name+"**\n"
        response+=str(self.getNumberSuccessfulJobs(jobs_ls))+" out of "+ str(num_jobs) +" are successful\n"
        response+=str(self.getNumberFailedJobs(jobs_ls))+" out of "+ str(num_jobs) +" are failures\n\n"
        # generate the main table and add it to the final response
        response+= self.generateMarkDownTable(jobs_ls[:10])
        return response

    # Markdown formatting method if jobs based on data type are searched for.
    def formatJobDataTypes(self, second_arg, jobs_ls_all):
        # Filter jobs based on given data type.
        jobs_ls = self.filterJobs(jobs_ls_all,False,second_arg)
        num_jobs = len(jobs_ls)
        # start response formatting (in Markdown)
        response="There are a total of "+str(num_jobs)+" jobs found for the data type: **"+second_arg+"**\n"
        response+=str(self.getNumberSuccessfulJobs(jobs_ls))+" out of "+ str(num_jobs) +" are successful\n"
        response+=str(self.getNumberFailedJobs(jobs_ls))+" out of "+ str(num_jobs) +" are failures\n\n"
        # generate the main table and add it to the final response
        response+= self.generateMarkDownTable(jobs_ls[:10])
        return response

    # Generates Markdown table for Job ID
    def formatJobId(self,job):
        job_json = json.loads(str(job))
        return "|Parameter|Value|\n|:------|:------|\n \
                    |Status|"+self.getJobStatus(job)+"|\n \
                    |Job ID|"+job.id+"|\n \
                    |Data Type|"+job.dataType+"|\n \
                    |Data|"+job.data+"|\n \
                    |PAP|"+str(job_json['pap'])+"\n \
                    |TLP|"+str(job_json['tlp'])+"\n \
                    |Created By|"+job_json['createdBy']+"|\n \
                    |Created At|"+str(job_json['createdAt'])+"|\n \
                    |Analyzer Name|"+job.analyzerName+"|\n \
                    |Analyzer ID|"+job.analyzerId+"|\n \
                    |Organization|"+job.organization+"|\n"

    # Specific printing formatting
    def addStartDate(self, job):
        job_json = json.loads(str(job))
        return "|Start Date|"+ str(job_json['startDate'])+"\n\n"

    # Generate Markdown table for Successful Job Report
    def formatSuccessfulJobReport(self,job):
        report = self.cortex_object.jobReport(job.id)
        taxonomies = report['summary']['taxonomies']
        if taxonomies == []:
            response = ":information_desk_person: No taxonomy found for job with ID:"+job.id+"\n"
        else:
            response = "## Summary Successful Job\n\n|Parameter|Value|\n|:-------|:-------|\n"
            response += "|Job ID|"+job.id+"|\n"
            response += "|Analyzer|"+job.analyzerName+"|\n"
            for k in taxonomies[0]:
                    response+= "|{}|{}|\n".format(k,taxonomies[0][k])
        response+="[:arrow_right: **Full Report**]("+link+"/index.html#!/jobs/"+job.id+")\n\n"
        response+="---\n"
        return response

    # Generate Markdown table for Failed Job Report
    def formatFailedJobReport(self,job):
        report = self.cortex_object.jobReport(job.id)
        response = "## Summary Unsuccessful Job\n\n|Parameter|Value|\n|:-------|:-------|\n"
        response += "|Job ID|"+job.id+"|\n"
        response += "|Analyzer|"+job.analyzerName+"|\n"
        # If error message is too long, cut it.
        error = report['errorMessage'].split('\n')[0]
        response += "|Error Message|"+error+"|\n"
        response += "[:arrow_right: **Full Report**]("+link+"/index.html#!/jobs/"+job.id+")\n\n"
        response+="---\n"
        return response

    # Wait for a job to be completed, this is used when the run command is given
    def waitForJob(self, job):
        i = 0
        if (not self.checkJobStatus(job)):
            # Wait for 15 minutes for the job to be done
            while(i<900):
                time.sleep(2)
                job = self.cortex_object.jobId(job.id)
                if (self.checkJobStatus(job)):
                    # If job is complete, return True
                    return (True,job)
                i += 2
            # If job is still running, return False
            return (False,job)
        else:
            return (True,job)

# Run Class, contains methods belonging to run jobs. Many of the methods in this class format and process the run request.
class Run:

    # Check if the force flag has been given. Change resp and return True if the flag is present.
    def forceFlag(self, resp):
        if resp[-1].lower()=="force":
            return (resp[:-1], 1)
        # Else flag is 0, return tuple flag and resp unchanged.
        else:
            return (resp,0)

    # Parse all the given arguments in case the user wants to run a job.
    def getArgs(self,resp):
        # Second argument must be a data type
        data_type_query = resp[2].lower()
        if not (data_type_query in run_ls):
            return ":no_entry: Careful, you entered an incompatible data type. Make sure the data type you are launching your job on is compatible: `/cortex help run`\n"
        # Third argument must be the actual data.
        data = resp[3].lower()
        # check if a tlp is given (optional fourth argument)
        try:
            if resp[4].lower() in dict_tlp:
                tlp = dict_tlp[resp[4].lower()]
                # Make sure the given argument is a valid TLP.
            else:
                return ":fearful: Oh no, you inserted an invalid TLP. Remember TLP is either white, green, amber or red\n"
        # If no TLP is given, default is 2 (amber).
        except:
            tlp = 2
        return (data_type_query,data,tlp)

    # Format method to check whether a job was found in the cache or not.
    def addCacheString(self,job):
        job_json = json.loads(str(job))
        cache = job_json.get("fromCache","")
        if cache != "":
            return "|From Cache|"+str(job_json['fromCache'])+"|\n \
                       |Start Date|"+ str(job_json['startDate'])+"|\n\n"
        else:
            return "|From Cache|False|\n \
                       |Start Date|N/A|\n\n"

    # Main run formating response method.
    def formatRunResponse(self, job):
        job_object=Job()
        analyzer_object = Analyzer()
        status_icon=job_object.getJobStatus(job)
        (check_job,job) = job_object.waitForJob(job)
        # If the job is still in progress, return
        if (not check_job):
            response = ":clock10: The job took more than 15 minutes to complete. Check `/cortex jobs` in a little bit. To see the full report\n\n[:arrow_right: **Full Report**]("+link+"/index.html#!/jobs/"+job.id+")\n\n"
            response += "---\n"
        else:
            # The job is completed, return information and summary.
            response = "\n\n## Job Initial Basic Information\n\n"+job_object.formatJobId(job)+self.addCacheString(job)
            if job.status == "Success":
                response += job_object.formatSuccessfulJobReport(job)
            else:
                response += job_object.formatFailedJobReport(job)
        return response

    # Generate the subprocess to run the jobs
    def callSubProcess(self,args_ls):
        pid = subprocess.Popen(args_ls,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        return ":chart_with_upwards_trend: Your Job is being processed, you will receive a private message when it is done! (This might take several minutes :sleeping: )\n"


# Help Class. Formats and returns the two possible help menu.
class Help():

    # Main help menu
    def mainHelp(self):
        # Simple markdown print output
        response="## :question: Welcome to Cortex Bot's Help Menu\n\n|**Description**|**Command**|\n|:--------|:------|\n \
            |For all enabled analyzers| `/cortex analyzers`|\n \
            |For more information on one specific analyzer| `/cortex analyzers [analyzer_name]`|\n \
            |If you are looking for analyzers supporting a certain data type*| `/cortex analyzers [data_type]`\n \
            |For all existing jobs| `/cortex jobs`|\n \
            |For all existing jobs belonging to a specific analyzer| `/cortex jobs [analyzer_name]`|\n \
            |For more information on one specific job| `/cortex jobs [job_id]`|\n \
            |If you are looking for all jobs ran on a specific data type*| `/cortex jobs [data_type]`|\n \
            |For a job's report| `/cortex jobs report [job_id]`|\n \
            |For a job's artifacts| `/cortex jobs artifacts [job_id]`|\n"
        response+="*Available data types: domain, ip, url, fqdn, uri_path, user-agent, hash, email, mail, mail_subject, registry, regexp, other, filename\n\n"
        response+="---\n"
        response+=":mega: **NOTE**: If you want to share an output to the whole channel, add `all` at the end of the `/cortex` command. By default, each query is only visible to you.\n"
        response+= "Example:`/cortex jobs all`\n\n"
        response+="---\n"
        response+=":information_source: If you would like to run an analyzer, please refer to the run help menu under `/cortex help run`\n\n"
        response+="---\n"
        response+=":heavy_check_mark: - Active/Success\n:x: - Locked/Failure\n:heavy_minus_sign: - InProgress/Waiting\n\n"
        response+="---\n"
        response+="[:arrow_right: **Click Here For Web UI**]("+link+")\n"
        return response

    # Run help menu
    def runHelp(self):
        # Simple markdown print output for help run menu
        response="## :globe_with_meridians: **Welcome to Cortex Bot's Run Menu**\n\n|**Description**|**Command**|\n|:--------|:------|\n \
             |To run a job| `/cortex run [analyzer name] [Data Type] [Data]` | \n \
             |To run a job with a specific TLP| `/cortex run [analyzer name] [Data Type] [Data] [TLP_Color]` | \n\n"
        response+="---\n"
        response+="#### :bangbang: Certain Things to Keep in Mind\n"
        response+="* If no TLP is specified, Cortex will run the job with TLP 2 (amber)\n"
        response+="* The TLP you give can only be a white (0), green (1), amber (2) or red (3)\n"
        response+="* So far, analyzers can only be run on `hash`,`domain`,`ip` or `url` data types. Other data types will not work\n"
        response+="* By default, when an analyzer is run, Cortex will check if the job already exists in its cache. To force cortex to fulfill a new job, insert `force` at the end of your command\n\n"
        response+="   Example: `/cortex run MISP_2_0 ip 8.8.8.8 force`\n\n"
        response+="---\n"
        response+=":bar_chart: **Want to run a job from the Web UI?**"
        response+="[   :arrow_right: **Click Here**]("+link+"/index.html#!/analyzers)\n"
        return response
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
    cortex_object=Cortex()
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
    job_object=Job()
    analyzer_object = Analyzer()
    cortex_object = Cortex()
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
    job_object=Job()
    analyzer_object = Analyzer()
    run_object = Run()
    cortex_object = Cortex()
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
            response = help_object.mainHelp()
        elif first_arg=="help" and resp[1].lower()=="run" and len(resp)==2:
            response = help_object.runHelp()
        else:
            response=":eyes: Invalid usage of the `/cortex` command. Please type `/cortex help` for more information or `/cortex help run` if you want to run a job"
    data = {"response_type":response_type,"text":response}
    json_data=json.dumps(data)
    return json_data

if __name__ == "__main__":
    print(main())
