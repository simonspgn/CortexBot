from .analyzer import Analyzer
from .job import Job
import subprocess
import json

# Run Class, contains methods belonging to run jobs. Many of the methods in this class format and process the run request.
class Run:

    def __init__(self,api,link):
        self.api = api
        self.link = link
        self.run_ls = ["domain","ip","url","hash"]


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
        if not (data_type_query in self.run_ls):
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
            response = "|From Cache|"+str(job_json['fromCache'])+"|\n"
            response+= "|Start Date|"+ str(job_json['startDate'])+"|\n\n"
        else:
            response = "|From Cache|False|\n"
            response+= "|Start Date|N/A|\n\n"
        return response

    # Main run formating response method.
    def formatRunResponse(self, job):
        job_object=Job(self.api,self.link)
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

