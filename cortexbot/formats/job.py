from .cortex import Cortex
import json
import time

# Job Class, contains methods belonging to job types. Many of the methods in this class format the markdown response returned to Mattermost.
class Job:

    def __init__(self,api,link):
      self.cortex_object=Cortex(api)
      self.link = link

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
            response+="|"+self.getJobStatus(job)+"|{}|{}|{}|{}|\n".format(job.id,job.analyzerName,job.dataType,"[**See Report**]("+self.link+"/index.html#!/jobs/"+job.id+")\n")
        response+="---\n"
        response+=":heavy_plus_sign: [**See all**]("+self.link+"/index.html#!/jobs)\n\n"
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
        response+="[:arrow_right: **Full Report**]("+self.link+"/index.html#!/jobs/"+job.id+")\n\n"
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
        response += "[:arrow_right: **Full Report**]("+self.link+"/index.html#!/jobs/"+job.id+")\n\n"
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