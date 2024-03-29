import json

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
        response="|Parameter|Value|\n|:------|:------|\n"
        response+= "|Name|"+analyzer.name+"|\n"
        response+= "|Base Config|"+analyzer.baseConfig+"|\n"
        response+= "|Description|"+analyzer.description+"|\n"
        response+= "|Data Types|"+', '.join(analyzer.dataTypeList)+"|\n"
        response+= "|ID|"+analyzer.id+"|\n"
        response+= "|Version|"+analyzer.version+"|\n"
        response+= "|Max TLP|" + str(analyzer_json['maxTlp']) +"|\n"
        response+= "|Max Pap|" + str(analyzer_json['maxPap']) +"|\n"
        response+= "|Author|"+analyzer.author+"|\n"
        response+= "|URL|"+analyzer.url+"|\n"
        response+= "|License|"+analyzer.license+"|\n"
        response+= "|Created By|"+analyzer.createdBy+"|\n"
        response+= "|Created At|"+str(analyzer_json['createdAt'])+"\n"
        return response
