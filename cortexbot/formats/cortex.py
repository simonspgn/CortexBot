# Cortex Class: Includes all the script's direct interactions with Cortex. Returns Lists, Jobs or Analyzers depending on Query.
class Cortex:

    def __init__(self,api):
        self.api = api

  # Method to get all enabled analyzers from Cortex
    def allAnalyzers(self):
        return self.api.analyzers.find_all({}, range='all')

    # Method to get all the analyzers that can run on a specific data type.
    def analyzerType(self,type):
        return self.api.analyzers.get_by_type(type)

    # Method to get an analyzer by name from Cortex
    def analyzerName(self,name):
        return self.api.analyzers.get_by_name(name)

    # Method to run an analyzer. Returns a job.
    def runByName(self,name,data_type,data,tlp,flag):
        return self.api.analyzers.run_by_name(name, {'data':data,'dataType':data_type,'tlp':tlp},force=flag)

    # Method to find all existing jobs from Cortex.
    def allJobs(self):
        return self.api.jobs.find_all({}, range='all')

    # Method to find the 10 most recent jobs from Cortex
    def limitedJobs(self):
        return self.api.jobs.find_all({}, range='0-10',sort='-createdAt')

    # Method to get a job's report from Cortex
    def jobReport(self,id):
        return self.api.jobs.get_report(id).report

    # Method to get a job by ID from Cortex.
    def jobId(self,id):
        return self.api.jobs.get_by_id(id)

    # Method to get a job's artifacts by ID from Cortex
    def jobArtifacts(self,id):
        return self.api.jobs.get_artifacts(id)
