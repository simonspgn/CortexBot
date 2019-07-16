# Help Class. Formats and returns the two possible help menu.
class Help():

    # Main help menu
    def mainHelp(self,link):
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
    def runHelp(self,link):
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


