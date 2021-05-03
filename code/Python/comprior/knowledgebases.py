from abc import abstractmethod
import math
from opentargets import OpenTargetsClient
from bioservices import KEGG, REST
import pandas as pd
import benchutils as util
import time, requests, json
from datetime import datetime
from lxml.html import fromstring
import pypath.core.network as network
import pypath.core.entity as entity
import pypath.internals.input_formats as input_formats


############################### WEB SERVICES ###############################

class ENRICHR(REST):
    """Queries some of the API endpoints of the EnrichR web service (https://maayanlab.cloud/Enrichr/help#api).

       :param config: configuration parameters for EnrichR web service (as specified in config file).
       :type config: dict
       """
    def __init__(self):
        self.config = util.getConfig("Enrichr")
        super().__init__("ENRICHR", url=self.config["webservice_uri"])

    def addlist(self, geneList):
        """Queries EnrichR to annotate a given list of genes.
           Returns a userListID, which can be used to retrieve the actual results in a second query.

           :param geneList: list of genes to annotate
           :type genes: list of str
           :return: json response containing a userListID.
           :rtype: dict of str
           """

        genesStr = ""
        for gene in geneList:
            genesStr += str(gene) + "\n"

        payload = {
            'list': (None, genesStr)
        }

        response = self.http_post('addList', files=payload, frmt="json")

        return response

    def export(self, params):
        """Download file of enrichment results.
           Requires a userListId that was retrieved from a prior query.

           :param params: list of parameters to use for that query (userListId: Identifier returned from addList endpoint, filename: Name of text file download, backgroundType: Gene set library for which to download results)
           :type params: list of str
           :return: text file containing enrichment results.
           :rtype: str
           """

        params["stream"] = "true"

        response = self.http_get("export", params = params)

        return response

    def genemap(self, params):
        """Finds all terms, their descriptions, and optional categorizations, for a given gene identifier.

           :param params: list of parameters to be used for the query (gene	Gene to use in search for terms, json (optional): Set "true" to return JSON rather plaintext, setup (optional): Set "true" to category information for the libraries)
           :type params: list of str
           :return: json object of all terms containing the specified gene and their descriptions.
           :rtype: dict of str
           """
        response = self.http_get("genemap", params = params)

        return response

    def enrich(self, params):
        """Returns all that are terms available in library (specified by backgroundType param) and enriched in the given set of genes (specified by userListId param).

            :param params: list of parameters to be used for the query (userListId: Identifier returned from addList endpoint; backgroundType: Gene set library to enrich against)
            :type params: list of str
            :return: dataframe object of all enriched terms (unsorted, unfiltered.
            :rtype: dataframe
            """

        response = self.http_get("enrich", params = params)
        res = pd.DataFrame.from_dict(list(response.values())[0])

        if not res.empty:
            res.columns = ["Rank", "Term name", "P-value", "Z-score", "Combined score", "Overlapping genes", "Adjusted p-value", "Old p-value", "Old adjusted p-value"]
            res = res[["Term name", "P-value", "Z-score", "Combined score", "Overlapping genes", "Adjusted p-value",
                 "Old p-value", "Old adjusted p-value"]]
        else:
            #create empty dataframe if we did not receive any results
            res = pd.DataFrame(columns=["Term name", "P-value", "Z-score", "Combined score", "Overlapping genes", "Adjusted p-value",
                 "Old p-value", "Old adjusted p-value"])
        return res


class UMLS_AUTH(REST):
    """Singleton class.
       Python code encapsulates it in a way that is not shown in Sphinx, so have a look at the descriptions in the source code.

       Authentication service to get access to the UMLS database UMLS database (which we need for retrieving CUI disease codes for querying DisGeNET).
       You first have to get a ticket-granting ticket (tgt, valid for 8 hours) with the help of an API key.
       With the tgt, you can then request a service ticket for every new query to the UMLS database.
       The service ticket must then be used for the query.
       The task of this class is to generate a valid tgt and subsequent service ticket.
       Documentation on the authentication process: https://documentation.uts.nlm.nih.gov/rest/authentication.html

       :param config: configuration parameters for UMLS web service as specified in config file.
       :type config: dict
       :param tgt_timestamp: timestamp of the tgt. If it is older than 8 hours, we need to request a new tgt.
       :type tgt_timestamp: str
       :param tgt: id of the ticket-granting ticket (valid for 8 hours). With this ticket, we can then query the actual UMLS web service.
       :type tgt: list of str
       :param service: uri for the service login
       :type service: str
       """
    class __UMLS_AUTH(REST):
        def __init__(self):
            self.config = util.getConfig("UMLS")
            self.tgt_timestamp = None
            self.tgt = None
            self.service = self.config["loginservice_uri"]
            super().__init__("UMLS_AUTH", url=self.config["login_uri"])

        def get_tgt(self):
            """Get a ticket-granting ticket (tgt) from the authentication service.

               :return: a valid tgt (valid for 8 hours).
               :rtype: str
               """
            # we use a different uri here, so use requests instead of the bioservices interface
            self.tgt_timestamp = datetime.now()

            params = {'apikey': self.config["apikey"]}
            r = self.http_post(self.config["auth_endpoint"], data=params)


            response = fromstring(r)
            ## extract the entire URL needed from the HTML form (action attribute) returned - looks similar to https://utslogin.nlm.nih.gov/cas/v1/tickets/TGT-36471-aYqNLN2rFIJPXKzxwdTNC5ZT7z3B3cTAKfSc5ndHQcUxeaDOLN-cas
            ## we make a POST call to this URL in the getst method
            #only extract the very last part of the uri
            tgt_str = response.xpath('//form/@action')[0]
            tgt = tgt_str.split("/")[-1]
            return tgt

        # authentication function: get the service ticket - valid for up to 8 minutes
        def get_st(self):
            """Get a service ticket from the authentication service (valid for 8 minutes), which can then be used in the actual query.
               In order to get a service ticket, a valid ticket-granting ticket (tgt) must be provided.
               If the last tgt is outdated, generate a new one.

               :return: service ticket.
               :rtype: str
               """
            # check if a valid tgt exists (expires after 8 hours)
            if self.tgt == None:
                # request new tgt
                self.tgt = self.get_tgt()
            elif (datetime.now() - self.tgt_timestamp).total_seconds() > 28800:
                # request new tgt
                self.tgt = self.get_tgt()

            params = {'service': self.service}
            h = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain",
                     "User-Agent": "python"}
            st = self.http_post(self.config["auth_endpoint"] + self.tgt, data=params)
            return st

    instance = None

    def __init__(self):
        if not UMLS_AUTH.instance:
            UMLS_AUTH.instance = UMLS_AUTH.__UMLS_AUTH()

    def __getattr__(self, name):
        return getattr(self.instance, name)

#web service for retrieven UMLS CUI codes for labels (DisGeNET requires CUIs)
class UMLS(REST):
    """Retrieves UMLS CUI codes for labels, which can then be used for querying DisGeNET.

       :param config: configuration parameters for UMLS web service (as specified in configuration file).
       :type config: dict
       :param auth: authentication component to generate a valid service ticket (required for every query).
       :type auth: :class:`UMLS_AUTH`
       """
    def __init__(self):
        self.config = util.getConfig("UMLS")
        self.auth = UMLS_AUTH()
        super().__init__("UMLS", url=self.config["webservice_uri"])

    def getCUIs(self, labels):
        """Get CUIs for the given labels.

           :param labels: list of identifiers for which to retrieve CUIs, e.g. disease names.
           :type labels: list of str
           :return: list of CUIs.
           :rtype: list of str
           """
        # do the actual request
        cuis = set()
        for label in labels:
            #get a valid service ticket
            params = {'ticket': self.auth.get_st()}
            query = "/search/current?string=" + label + "&searchType=exact"

            response = self.http_get(query, params = params)

            #get CUIs out of response
            results = response["result"]["results"]
            label_cuis = []
            for result in results:
                label_cuis.append(result["ui"])
            cuis.update(label_cuis)

        return list(cuis)

class DISGENET(REST):
    """Queries the DisGeNET web service for a given set of labels and retrieves association scores for all genes related to the query labels.
       DisGeNET API documentation: https://www.disgenet.org/api/

       :param umls: list of gene names to be mapped
       :type umls: :class:`UMLS` for transforming disease names to CUIs (required for query)
       """
    def __init__(self):
        self.umls = UMLS()
        super().__init__("DisGeNET", url=util.config["DisGeNET"]["webservice_url"])

    def getVersion(self):
        """Get the current version of the DisGeNET API endpoint.

           :return: web service version infos.
           :rtype: json dict
           """
        ret = self.http_get("/version")
        return ret

    def query(self, labels):
        """Conducts the actual query to retrive gene-disease association scores for a given list of disease labels.
           Transforms the disease labels into CUIs before with the UMLS web service.

           :param labels: list of disease labels for which to retrieve gene-disease associations.
           :type labels: list of str
           :return: DataFrame with gene-disease association scores.
           :rtype: :class:`pandas.DataFrame`
           """
        cuis = self.umls.getCUIs(labels)

        cui_string = ""
        cui_string += "%2C".join(cuis)
        requestString = "/gda/disease/" + cui_string
        ret = None
        #retry query until we have to wait too long. DisGeNET sometimes seems to be quite slow
        while self.TIMEOUT < 250 and ret == None:
            print("Trying to connect to DisGeNET...")
            ret = self.http_get(requestString)
            self.TIMEOUT += 30

        #check if 500 is returned
        if isinstance(ret, int):
            return pd.DataFrame(columns=["gene_symbol", util.config["DisGeNET"]["associationScore"]])

        # bring the result into a readable format
        results = pd.DataFrame(ret)
        try:#if the dataframe is empty, just return an empty dataframe
            reduced_results = results.loc[:, ["gene_symbol", util.config["DisGeNET"]["associationScore"]]]
        except:
            return pd.DataFrame(columns=["gene_symbol", util.config["DisGeNET"]["associationScore"]])

        reduced_results.columns = ["gene_symbol", "score"]

        #save the results in an intermediate file
        dir_name = util.config["DisGeNET"]["outputDir"] + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "/"
        util.createDirectory(dir_name)
        filename = "queryResults.csv"

        reduced_results.to_csv(dir_name + filename, sep = ",", index = False)

        #map gene IDs to the desired format if necessary
        desiredIDFormat = util.config["Dataset"]["finalGeneIDFormat"]
        if desiredIDFormat != "HGNC":
            outputFile = dir_name + "mapped_" + "HGNC_" + desiredIDFormat + "/" + filename
            util.createDirectory(dir_name + "mapped_" + "HGNC_" + desiredIDFormat + "/")
            reduced_results = util.mapRanking(reduced_results, "HGNC", desiredIDFormat, outputFile)


        return reduced_results

class GCONVERT():
    """Queries the g:Convert web service to map a list of identifiers to a desired format.
       g:Convert makes use of the Ensembl build.
       g:Convert API documentation: https://biit.cs.ut.ee/gprofiler/page/apis

       :param url: API url as specified in the configuration file.
       :type url: str
       """
    def __init__(self):
        self.url = util.config["gConvert"]["webservice_url"]
        self.name = "GCONVERT"

    def query(self, items, originalFormat, desiredFormat):
        """Map a list of itendifiers to the desired format.

           :param items: list of identifiers to be mapped
           :type items: list of str
           :param originalFormat: current format of the identifiers
           :type originalFormat: str
           :param desiredFormat: desired identifier format
           :type desiredFormat: str
           :return: DataFrame containing the identifier mapping.
           :rtype: :class:`pandas.DataFrame`
           """
        mapping = None
        r = requests.post(
            url=self.url,
            json={
                'organism': 'hsapiens',
                'target': desiredFormat,
                'query': items,
            }
        )
        result = r.json()['result']
        desireds = list()
        originals = list()
        for item in result:
            desireds.append(item["converted"])
            originals.append(item["incoming"])
        mapping = pd.DataFrame({originalFormat: originals, desiredFormat: desireds})
        return mapping



class PATHWAYCOMMONSWS(REST):
    """Queries the PathwayCommons web service.
       Bioservices' existing implementation to query PathwayCommons was not used because it contained outdated values for _valid_formats for pathway retrieval,
       so we used the original code and adapted it to work correctly.
       """
    def __init__(self):
        self.easyXMLConversion = False
        self._default_extension = "json"
        super().__init__("PathwayCommonsWS", url=util.config["PathwayCommons"]["webservice_url"])

    _valid_direction = ["BOTHSTREAM", "DOWNSTREAM", "UPSTREAM"]
    def getVersion(self):
        """Map a list of genes to the desired format.

           :param genes: list of gene names to be mapped
           :type genes: list of str
           :return: list of mapped gene names.
           :rtype: list of str
           """
        ret = self.http_get("/version")
        return ret

    # just a get/set to the default extension
    def _set_default_ext(self, ext):
        """Map a list of genes to the desired format.

           :param genes: list of gene names to be mapped
           :type genes: list of str
           :return: list of mapped gene names.
           :rtype: list of str
           """
        self.devtools.check_param_in_list(ext, ["json", "xml"])
        self._default_extension = ext

    def _get_default_ext(self):
        """Map a list of genes to the desired format.

           :param genes: list of gene names to be mapped
           :type genes: list of str
           :return: list of mapped gene names.
           :rtype: list of str
           """
        return self._default_extension

    default_extension = property(_get_default_ext, _set_default_ext,
                                     doc="set extension of the requests (default is json). Can be 'json' or 'xml'")

    def search(self, q, page=0, datasource=None, organism=None, type=None):
        """Text search in PathwayCommons using Lucene query syntax

        Some of the parameters are BioPAX properties, others are composite
        relationships.

        All index fields are (case-sensitive): comment, ecnumber,
        keyword, name, pathway, term, xrefdb, xrefid, dataSource, and organism.

        The pathway field maps to all participants of pathways that contain
        the keyword(s) in any of its text fields.

        Finally, keyword is a transitive aggregate field that includes all
        searchable keywords of that element and its child elements.

        All searches can also be filtered by data source and organism.

        It is also possible to restrict the domain class using the
        'type' parameter.

        This query can be used standalone or to retrieve starting points
        for graph searches.


        :param str q: requires a keyword , name, external identifier, or a
            Lucene query string.
        :param int page: (N>=0, default is 0), search result page number.
        :param str datasource: filter by data source (use names or URIs of
            pathway data sources or of any existing Provenance object). If
            multiple data source values are specified, a union of hits from
            specified sources is returned. datasource=[reactome,pid] returns
            hits associated with Reactome or PID.
        :param str organism: The organism can be specified either by
            official name, e.g. "homo sapiens" or by NCBI taxonomy id,
            e.g. "9606". Similar to data sources, if multiple organisms
            are declared a union of all hits from specified organisms
            is returned. For example organism=[9606, 10016] returns results
            for both human and mice.
        :param str type: BioPAX class filter
        """
        if self.default_extension == "xml":
            url = "search.xml?q=%s"  % q
        elif self.default_extension == "json":
            url = "search.json?q=%s"  % q

        params = {}
        if page>0:
            params['page'] = page
        else:
            self.logging.warning("page should be >=0")

        if datasource:
            params['datasource'] = datasource

        if type:
            params['type'] = type

        if organism:
            params['organism'] = organism

        res = self.http_get(url, frmt=self.default_extension,
                params=params)

        if self.default_extension == "xml":
            res = self.easyXML(res)

        return res


    def get(self, uri, frmt="BIOPAX"):
        """Retrieves full pathway information for a set of elements

        elements can be for example pathway, interaction or physical
        entity given the RDF IDs. Get commands only
        retrieve the BioPAX elements that are directly mapped to the ID.
        Use the :meth:`traverse` query to traverse BioPAX graph and
        obtain child/owner elements.

        :param str uri: valid/existing BioPAX element's URI (RDF ID; for
            utility classes that were "normalized", such as entity refereneces
            and controlled vocabularies, it is usually a Identifiers.org URL.
            Multiple IDs can be provided using list
            uri=[http://identifiers.org/uniprot/Q06609,
            http://identifiers.org/uniprot/Q549Z0']
            See also about MIRIAM and Identifiers.org.
        :param str format: output format (values)

        :return: a complete BioPAX representation for the record
            pointed to by the given URI is returned. Other output
            formats are produced by converting the BioPAX record on
            demand and can be specified by the optional format
            parameter. Please be advised that with some output formats
            it might return "no result found" error if the conversion is
            not applicable for the BioPAX result. For example,
            BINARY_SIF output usually works if there are some
            interactions, complexes, or pathways in the retrieved set
            and not only physical entities.
        """

        # validates the URIs
        if isinstance(uri, str):
            url = "get?uri=" +uri
        elif isinstance(uri, list):
            url = "get?uri=" +uri[0]
            if len(uri)>1:
                for u in uri[1:]:
                    url += "&uri=" + u

        if frmt != "BIOPAX":
            url += "&format=%s" % frmt

        res = self.http_get(url)

        return res


class KnowledgeBaseFactory():#singleton class
    """Singleton class.
       Python code encapsulates it in a way that is not shown in Sphinx, so have a look at the descriptions in the source code.

       Creates knowledge bases based on the provided name and creates all corresponding objects, e.g. web service endpoints.
       Every knowledge base implementation must be registered here, otherwise it will not be accessible.
       """
    class __KnowledgeBaseFactory():
        def createKnowledgeBase(self, knowledgebase):
            """Creates knowledge base based on a given name.

               :param knowledgebase: name of the knowledge base to be created.
               :type knowledgebase: str
               :return: knowledge base object.
               :rtype: :class:`KnowledgeBase` or inheriting classes
               """
            if knowledgebase == "DisGeNET":
                return Disgenet()
            if knowledgebase == "KEGG":
                #create a pathway mapper
                pathwayparser = KEGGPathwayParser()
                return Kegg(pathwayparser)
            if knowledgebase == "Enrichr":
                return Enrichr()
            if knowledgebase == "OpenTargets":
                return OpenTargets()
            if knowledgebase == "PathwayCommons":
                return Pathwaycommons()
            if knowledgebase == "Biomart":
                return BioMART()
            if knowledgebase == "gConvert":
                return Gconvert()

            print("The listed knowledge base is not available. See the documentation for available knowledge bases.")
            exit()

    instance = None

    def __init__(self):
        if not KnowledgeBaseFactory.instance:
            KnowledgeBaseFactory.instance = KnowledgeBaseFactory.__KnowledgeBaseFactory()

    def __getattr__(self, name):
        return getattr(self.instance, name)


############################### KNOWLEDGE BASES ###############################

class KnowledgeBase:
    """Super class for every knowledge base implementation.
       If a new knowledge base is implemented, it must inherit from this class and implement methods :meth:`KnowledgeBase.getRelevantGenes()`, :meth:`KnowledgeBase.getGeneScores()`, and :meth:`KnowledgeBase.getRelevantPathways()`.

       :param name: name of the knowledge base
       :type name: str
       :param config: configuration parameter of the knowledge base as specified in the config file.
       :type config: dict
       :param webservice: web service querying object
       :type webservice: :class:`bioservices.REST` or inheriting classes.
       :param hasGeneInformation: true if the knowledge base provides gene association information, false otherwise
       :type hasGeneInformation: bool
       :param hasPathwayInformation: true if the knowledge base also provides pathway information, false otherwise
       :type hasPathwayInformation: bool
       """

    def __init__(self, name, kb_config, webservice, geneInfo, pathwayInfo):
        self.name = name
        self.config = kb_config
        util.createDirectory(self.config["outputDir"])
        self.webservice = webservice
        self.hasGeneInformation = geneInfo
        self.hasPathwayInformation = pathwayInfo
        super().__init__()

    @abstractmethod
    def getRelevantGenes(self, labels):
        """Abstract.
           Get all genes that are associated to a list of labels, e.g. disease names.

           :param labels: list of labels for which to retrieve the genes.
           :type labels: list of str
           :return: list of associated genes.
           :rtype: list of str
           """
        pass

    @abstractmethod
    def getGeneScores(self, labels):
        """Abstract.
           Get all genes and their association scores for a given list of disease names.

           :param labels: list of disease names for which to get gene-disease-association scores.
           :type labels: list of str
           :return: DataFrame of genes and their association scores.
           :rtype: :class:`pandas.DataFrame`
           """
        pass

    @abstractmethod
    def getRelevantPathways(self, labels):
        """Get all pathways related to a set of labels, e.g disease names.

           :param labels: list of labels for which to find related pathways.
           :type labels: list of str
           :return: dict of pathway names and pathway representations.
           :rtype: dict with :class:`pypath.Network` as values
           """
        pass

    def getName(self):
        """Returns the name of the knowledge base.

           :return: knowledge base name.
           :rtype: str
           """
        return self.name

    def hasPathways(self):
        """Returns if knowledge base retrieves pathway information, i.e. if :meth:`KnowledgeBase.getRelevantPathways()` is implemented..

           :return: true if knowledge base provides pathway information, false otherwise.
           :rtype: bool
           """
        return self.hasPathwayInformation

    def hasGenes(self):
        """Returns if knowledge base retrieves gene information, i.e. if :meth:`KnowledgeBase.getRelevantGenes()` :meth:`KnowledgeBase.getGeneScores()` are implemented.

           :return: true if knowledge base provides gene information, false otherwise.
           :rtype: bool
           """
        return self.hasGeneInformation


class Enrichr(KnowledgeBase):
    """Special knowledge base not intended to be used by feature selection approaches.
       Instead, it is used for evaluation purposes to annotate and enrich rankings.

       :param name: name of the knowledge base
       :type name: str
       :param config: configuration parameter of the knowledge base as specified in the config file.
       :type config: dict
       :param webservice: web service querying object
       :type webservice: :class:`bioservices.REST` or inheriting classes.
       :param hasGeneInformation: true if the knowledge base provides gene association information, false otherwise
       :type hasGeneInformation: bool
       :param hasPathwayInformation: true if the knowledge base also provides pathway information, false otherwise
       :type hasPathwayInformation: bool
       """
    def __init__(self):
        super().__init__("Enrichr", util.getConfig("Enrichr"), ENRICHR(), False, False)

    def downloadEnrichedTerms(self, userIdList, filePrefix):
        """Downloads enriched terms from a former query into a file.
           Filters these terms for those with an adjusted p-value > 0.05, then sorts by combined score in descending order.

           :param userIdList: userIdList to retrieve enrichment/annotation results from the original query.
           :type userIdList: str
           :param filePrefix: prefix to use in filename.
           :type filePrefix: str
           """
        geneSetLibrary = self.config["geneSetLibrary"]

        outputDir = self.config["outputDir"] + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "/"
        util.createDirectory(outputDir)
        outputFile = filePrefix + "_enrichedTerms.txt"

        params = {"userListId": str(userIdList), "backgroundType": geneSetLibrary}
        response = self.webservice.enrich(params)
        # first, filter enriched terms by q-score > 0.05
        # second, order by combined score in descending order
        # see also this best practices recommendation: https://www.researchgate.net/post/Enrichr_what_value_of_combined_score_is_significant
        final_terms = response[(response["Adjusted p-value"] < 0.05)]
        final_terms.sort_values(by = "Combined score", ascending = False, inplace = True)

        final_terms.to_csv(outputFile, sep = "\t", index = False)

    def getRelevantGenes(self, labels):
        """Is not implemented for EnrichR.

           :param labels: list of gene names to be mapped
           :type labels: list of str
           :return: :class:`NotImplementedError` as this knowledge base is not intended to be used for such analyses.
           :rtype: :class:`NotImplementedError`
           """
        raise NotImplementedError("EnrichR is currently only used for subsequent annotation and not intended to be used during analysis.")

    def getGeneScores(self, labels):
        """Is not implemented for EnrichR.

           :param labels: list of gene names to be mapped
           :type labels: list of str
           :return: :class:`NotImplementedError` as this knowledge base is not intended to be used for such analyses.
           :rtype: :class:`NotImplementedError`
           """
        raise NotImplementedError("EnrichR is currently only used for subsequent annotation and not intended to be used during analysis.")

    def getRelevantPathways(self, labels):
        """Is not implemented for EnrichR.

           :param labels: list of labels for which to find related pathways.
           :type labels: list of str
           :return: :class:`NotImplementedError` as this knowledge base is not intended to be used for such analyses.
           :rtype: :class:`NotImplementedError`
           """
        raise NotImplementedError("EnrichR is currently only used for subsequent annotation and not intended to be used during analysis.")

    def enrichGeneset(self, geneList, filePrefix):
        """Sends a list of identifies (here, genes) to EnrichR web service and stores all term enrichments in a file.

           :param geneList: list of gene names for which to retrieve enrichments.
           :type geneList: list of str
           :param filePrefix: prefix to use in file name (to store enrichments).
           :type filePrefix: str
           """

        #submit list for analysis
        data = self.webservice.addlist(geneList)
        userListID = data["userListId"]

        #download files of enriched terms
        self.downloadEnrichedTerms(userListID, filePrefix)

    def annotateGene(self, gene):
        """Annotates a gene with terms.

           :param gene: gene name.
           :type gene: str
           :return: list of all annotations to the provided gene.
           :rtype: list of str
           """

        params = {"json": "true", "setup": "true", "gene": gene}

        response = self.webservice.genemap(params)

        try:
            annotations = response["gene"]
            geneSetLibrary = self.config["geneSetLibrary"]
            annotation = annotations[geneSetLibrary]
        except:
            #no annotation was found
            annotation = []

        return annotation

    def annotateGenes(self, geneList, filePrefix):
        """Annotates a list of genes with relevant terms.

           :param geneList: list of gene names to annotate.
           :type geneList: list of str
           :param filePrefix: prefix to use when storing results in a file.
           :type filePrefix: str
           :return: dict of gene names and lists of their annotations.
           :rtype: dict
           """
        annotations = {}
        # if false then annotate each gene individually
        for gene in geneList:
            annotations[gene] = self.annotateGene(gene)

        outputDir = self.config["outputDir"] + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "/"
        util.createDirectory(outputDir)
        outputFile = filePrefix + "_annotatedGenes.txt"

        # write gene annotations to file
        with open(outputFile, 'w') as f:
            f.write("attributeName\tannotation\n")
            for gene, annotation in annotations.items():
                anno = ",".join(annotation)
                g = str(gene)
                if anno != "":
                    f.write(g + "\t" + anno + "\n")

        return annotations

class BioMART():
    """Maps a identifiers or data sets with identifiers to the desired format by using BiomaRt.
       Wrapper class that internally invokes BiomaRt's R code.
       Very unstable, so currently not used.
       However, it can be exchanged in :meth:`benchutils.retrieveMappings()` function.
       """

    def mapItems(self, itemList, originalFormat, desiredFormat):
        """Map a list of identifiers to the desired format.
           Internally invokes external R code that uses the BiomaRt package.

           :param itemList: list of identifiers to be mapped
           :type itemList: list of str
           :param originalFormat: original identifier format.
           :type originalFormat: str
           :param desiredFormat: format to which to map identifiers.
           :type desiredFormat: str
           :return: mapping data frame of identifiers (with original and desired format)
           :rtype: :class:`pandas.DataFrame`
           """
        # write results into intermediate file
        outputDir = util.getConfigValue("Biomart", "outputDir") + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "/"
        util.createDirectory(outputDir)
        util.createDirectory(outputDir + "input/")
        util.createDirectory(outputDir + "output/")
        filename = "mapping.csv"

        #put itemList into input file
        with open(outputDir + "input/" + filename, "w") as f:
            for item in itemList:
                f.write("%s\n" % item)

        params = [originalFormat, desiredFormat, outputDir + "input/" + filename, outputDir + "output/" + filename]
        util.runRCommand(util.getConfig("R"), "IdentifierMapping.R", params)
        mappedItems = pd.read_csv(outputDir + "output/" + filename)
        return mappedItems

    def getRelevantGenes(self, labels):
        """Is not implemented for BiomaRt.

           :param labels: list of gene names to be mapped
           :type labels: list of str
           :return: :class:`NotImplementedError` as this knowledge base is not intended to be used for such analyses.
           :rtype: :class:`NotImplementedError`
           """
        raise NotImplementedError("Biomart is currently only used for identifier mapping and not intended to be used during analysis.")

    def getGeneScores(self, labels):
        """Is not implemented for BiomaRt.

           :param labels: list of gene names to be mapped
           :type labels: list of str
           :return: :class:`NotImplementedError` as this knowledge base is not intended to be used for such analyses.
           :rtype: :class:`NotImplementedError`
           """
        raise NotImplementedError(
            "Biomart is currently only used for identifier mapping and not intended to be used during analysis.")

    def getRelevantPathways(self, labels):
        """Is not implemented for BiomaRt.

           :param labels: list of labels for which to find related pathways.
           :type labels: list of str
           :return: :class:`NotImplementedError` as this knowledge base is not intended to be used for such analyses.
           :rtype: :class:`NotImplementedError`
           """
        raise NotImplementedError(
            "Biomart is currently only used for identifier mapping and not intended to be used during analysis.")

class Gconvert(KnowledgeBase):
    """Maps identifiers or data sets containing identifiers to the desired format by using the g:Convert web service.

       :param name: name of the knowledge base
       :type name: str
       :param config: configuration parameter of the knowledge base as specified in the config file.
       :type config: dict
       :param webservice: web service querying object.
       :type webservice: :class:`bioservices.REST` or inheriting classes
       :param hasGeneInformation: true if the knowledge base provides gene association information, false otherwise
       :type hasGeneInformation: bool
       :param hasPathwayInformation: true if the knowledge base also provides pathway information, false otherwise
       :type hasPathwayInformation: bool
       """
    def __init__(self):
        super().__init__("gConvert", util.getConfig("gConvert"), GCONVERT(), False, False)


    def mapItems(self, itemList, originalFormat, desiredFormat):
        """Map a list of identifiers to the desired format.

           :param itemList: list of identifiers to be mapped.
           :type itemList: list of str
           :param originalFormat: current format of the identifiers.
           :type originalFormat: str
           :param desiredFormat: desired format to which to map identifiers.
           :type desiredFormat: str
           :return: DataFrame table containing mappings of the identifiers from original to desired format.
           :rtype: :class:`pandas.DataFrame`
           """
        # write results into intermediate file
        mapping = self.webservice.query(itemList, originalFormat, desiredFormat)
        #remove nans in mapping
        indexNames = mapping[mapping[desiredFormat] == 'nan'].index
        mapping = mapping.drop(indexNames)
        return mapping

    def getRelevantGenes(self, labels):
        """Is not implemented for g:Convert.

           :param labels: list of gene names to be mapped
           :type labels: list of str
           :return: :class:`NotImplementedError` as this knowledge base is not intended to be used for such analyses.
           :rtype: :class:`NotImplementedError`
           """
        raise NotImplementedError("g:Convert is currently only used for identifier mapping and not intended to be used during analysis.")

    def getGeneScores(self, labels):
        """Is not implemented for g:Convert.

           :param labels: list of gene names to be mapped
           :type labels: list of str
           :return: :class:`NotImplementedError` as this knowledge base is not intended to be used for such analyses.
           :rtype: :class:`NotImplementedError`
           """
        raise NotImplementedError(
            "g:Convert is currently only used for identifier mapping and not intended to be used during analysis.")

    def getRelevantPathways(self, labels):
        """Is not implemented for g:Convert.

           :param labels: list of labels for which to find related pathways.
           :type labels: list of str
           :return: :class:`NotImplementedError` as this knowledge base is not intended to be used for such analyses.
           :rtype: :class:`NotImplementedError`
           """
        raise NotImplementedError(
            "g:Convert is currently only used for identifier mapping and not intended to be used during analysis.")



class OpenTargets(KnowledgeBase):
    """Knowledge base implementation of OpenTargets.
       Uses the OpenTargetsClient Python implementation provided by OpenTargets to query the web service API.

       :param name: name of the knowledge base
       :type name: str
       :param config: configuration parameter of the knowledge base as specified in the config file.
       :type config: dict
       :param webservice: web service querying implementation.
       :type webservice: :class:`opentargets.OpenTargetsClient`
       :param hasGeneInformation: true if the knowledge base provides gene association information, false otherwise
       :type hasGeneInformation: bool
       :param hasPathwayInformation: true if the knowledge base also provides pathway information, false otherwise
       :type hasPathwayInformation: bool
       """
    def __init__(self):
        super().__init__("OpenTargets", util.getConfig("OpenTargets"), OpenTargetsClient(), True, False)

    def getAssociations(self, labels):
        """Get all relevant information for a given set of labels, sorted by their association scores in descending order.
           Writes web service results into an intermediate file and maps the identifiers to have the correct format for further processing.

           :param labels: list of labels, e.g. disease names.
           :type labels: list of str
           :return: DataFrame containing all related genes and their association scores.
           :rtype: :class:`pandas.DataFrame`
           """

        cols = ["gene_symbol", "score"]
        associated_genes = pd.DataFrame(columns=cols)
        for term in labels:
            try:
                a_for_disease = self.webservice.get_associations_for_disease(term)
            except:
                print("SEEMS SOME ERROR OCCURED FOR " + term)
                continue
            #check if an error code was returned
            if isinstance(a_for_disease, int):
                print("ERROR: " + str(a_for_disease) + " RETURNED.")
                continue
            geneIDs = list()
            assocscores = list()
            for a in a_for_disease:
                geneID = a["id"]
                #the ID is currently attached by an EFO ID - remove it
                geneID = geneID.split("-")[0]
                geneIDs.append(geneID)
                score = a['association_score']['overall']
                assocscores.append(score)

            associated_genes = pd.DataFrame({"gene_symbol": geneIDs, "score": assocscores})

        #write results into intermediate file
        outputDir = util.getConfigValue("OpenTargets", "outputDir") + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "/"
        util.createDirectory(outputDir)
        outputFile = "genes.csv"
        associated_genes.to_csv(outputDir + outputFile, sep = ",", index = False)
        # check if gene ID format from expression data set matches OpenTargets' Ensembl Gene ID format
        desiredIDFormat = util.config["Dataset"]["finalGeneIDFormat"]
        #if desiredIDFormat != "ensembl_gene_id":
        if desiredIDFormat != "ENSG":
            outputFile = outputDir + "mapped_" + "ENSG_" + desiredIDFormat + "/" + outputFile
            util.createDirectory(outputDir + "mapped_" + "ENSG_" + desiredIDFormat + "/")
            associated_genes = util.mapRanking(associated_genes, "ENSG", desiredIDFormat, outputFile)

        #order by score
        associated_genes.sort_values('score', ascending=False, inplace=True)
        #remove duplicates
        associated_genes = associated_genes.drop_duplicates(subset = "gene_symbol")
        return associated_genes

    def getRelevantGenes(self, labels):
        """Get all genes that are somehow associated to the given labels, e.g. disease names.

           :param labels: list of identifiers, e.g. disease names, for which to find associated genes.
           :type labels: list of str
           :return: list of associated genes.
           :rtype: list of str
           """

        genes = self.getAssociations(labels)

        return list(genes.loc[:,"gene_symbol"].unique())

    def getGeneScores(self, labels):
        """Get all genes and their association scores that are related to the given labels, e.g. disease names.

           :param labels: list of identifiers, e.g. disease names, for which to find associated genes.
           :type labels: list of str
           :return: DataFrame of associated genes and their association scores, in descending order.
           :rtype: :class:`pandas.DataFrame`
           """
        geneScores = self.getAssociations(labels)
        return geneScores


    def getRelevantPathways(self, labels):
        """As OpenTargets currently does not provide pathway information, this feature is not implemented for OpenTargets.

           :param labels: list of labels for which to find related pathways.
           :type labels: list of str
           :return: :class:`NotImplementedError` as this knowledge base is not intended to be used for such analyses.
           :rtype: :class:`NotImplementedError`
           """
        raise NotImplementedError("OpenTargets cannot return pathways at the moment (although they also provide references to pathways, but this feature is not supported in the API.")


class Kegg(KnowledgeBase):
    """Knowledge base implementation for KEGG.
       Uses the KEGG web service implementation provided by bioservices.
       Requires an instance of :class:`KEGGPathwayParser` to be able to map retrieved pathways into the internal pathway format.

       :param name: name of the knowledge base
       :type name: str
       :param config: configuration parameter of the knowledge base as specified in the config file.
       :type config: dict
       :param webservice: web service querying implementation.
       :type webservice: :class:`opentargets.OpenTargetsClient`
       :param hasGeneInformation: true if the knowledge base provides gene association information, false otherwise
       :type hasGeneInformation: bool
       :param hasPathwayInformation: true if the knowledge base also provides pathway information, false otherwise
       :type hasPathwayInformation: bool
       :param pathwayparser: pathway mapping class that transforms KEGG pathways in SIF format into the internally used pathway format.
       :type pathwayparser: :class:`KEGGPathwayParser`
       """

    def __init__(self, pathwayparser):
        self.pathwayparser = pathwayparser
        super().__init__("KEGG", util.getConfig("KEGG"), KEGG(), True, True)

    def getPathwayNames(self, labels):
        """Retrieve all pathway names related to the given labels, e.g. disease names.

           :param labels: list labels, e.g. disease names, for which to find pathways.
           :type labels: list of str
           :return: list of pathway names.
           :rtype: list of str
           """

        pathways = []
        for label in labels:
            pathwayListString = self.webservice.find("pathway", "\"" + label + "\"")
            # pathway are returned in the form path:pathwayid\tdescription\n
            if pathwayListString == "\n" or isinstance(pathwayListString, int):
                pathwayList = []
                #print("EMPTY PATHWAYS:" + str(pathwayListString))
            else:
                pathwayList = pathwayListString.split("\n")[:-1]
            count = 0
            for pathway in pathwayList:
                if count <= int(self.config["maxNumPathways"]):
                    count += 1
                    # strip off the path prefix
                    pathwayName = pathway.split("\t")[0]
                    pathwayName = pathwayName[5:]
                    # replace "map" by "hsa" (because we want the reference organisms for homo sapiens)
                    pathwayName = pathwayName.replace("map", "hsa")
                    pathways.append(pathwayName)
                else:
                    break
        return pathways

    def getRelevantGenes(self, labels):
        """Get all genes that are related to a set of labels, e.g. disease names.
           For KEGG, this means we retrieve all genes that are contained in pathways associated to these labels.

           :param labels: list of identifiers, e.g. disease names, for which to find associated genes.
           :type labels: list of str
           :return: list of associated genes.
           :rtype: list of str
           """
        pathways = self.getRelevantPathways(labels)
        genes = set()
        for pathway in pathways.values():
            nodes = pathway.nodes
            for node in nodes.values():
                genes.add(node.label)

        #write genes to file
        outputDir = util.getConfigValue("KEGG", "outputDir") + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "/"
        util.createDirectory(outputDir)
        filename = "queryResults.txt"
        with open(outputDir + filename, 'w') as f:
            f.write("attributeName,score\n")
            f.write(",0.0\n".join(genes))

        return genes

    def getGeneScores(self, labels):
        """Get association scores for all genes that are related to the provided labels, e.g. disease names.
           For KEGG, the association score for a gene is the sum of its degree percentile rank for every pathway, normalized by the overall number of pathways retrieved.
           This favors hub genes/genes having many interactions with other genes.

           :param labels: list of identifiers, e.g. disease names, for which to find associated genes.
           :type labels: list of str
           :return: DataFrame of associated genes and their association scores, in descending order.
           :rtype: :class:`pandas.DataFrame`
           """
        pathways = self.getRelevantPathways(labels)
        overallCount = len(pathways)
        occurrenceCounts = {}
        for pathway in pathways.values():
            nodes = pathway.nodes
            interactions = pathway.interactions_by_nodes
            reduced_interactions = {}
            #update interactions to only store the interactions counts
            for entity in interactions.keys():
                reduced_interactions[entity.label] = len(interactions[entity])
            #make dataframe from count
            interactions_df = pd.DataFrame.from_dict(reduced_interactions, orient = 'index')
            interactions_df.columns = ["degree"]
            percentiles = interactions_df["degree"].rank(method='min', pct = True)
            for item in percentiles.iteritems():
                perc_score = item[1]
                feature = item[0]
                if feature in occurrenceCounts.keys():
                    occurrenceCounts[feature] += perc_score
                else:
                    occurrenceCounts[feature] = perc_score

        genes = list()
        scores = list()
        for geneID in occurrenceCounts.keys():
            genes.append(geneID)
            score = occurrenceCounts[geneID] / overallCount
            scores.append(score)

        geneScores = pd.DataFrame({"gene_symbol": genes, "score": scores})
        geneScores.sort_values("score", inplace=True, ascending = False)
        #write genes to file
        outputDir = util.getConfigValue("KEGG", "outputDir") + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + "/"
        util.createDirectory(outputDir)
        filename = "queryResults.txt"
        geneScores.to_csv(outputDir + filename, sep = ",", index = False)

        return geneScores

    def getRelevantPathways(self, labels):
        """Get all pathways related to a set of labels, e.g. disease names.
           Uses the :class:`KEGGPathwayParser` to map KEGG's pathways from SIF to :class:`pypath.Network`.

           :param labels: list of gene names to be mapped
           :type labels: list of str
           :return: dict of pathway names and their internal representation as :class:`pypath.Network`.
           :rtype: dict
           """
        pathway_graphs = {}

        pathways = []
        pathway_graphs = {}
        for label in labels:
            pathwayListString = self.webservice.find("pathway", "\"" + label + "\"")
            # pathway are returned in the form path:pathwayid\tdescription\n
            if ((pathwayListString == "\n") or (isinstance(pathwayListString, int)) or (pathwayListString is None)):
                pathwayList = []
                #print("EMPTY PATHWAYS:" + str(pathwayListString))
            else:
                pathwayList = pathwayListString.split("\n")[:-1]
            count = 0
            for pathway in pathwayList:
                # strip off the path prefix
                pathwayName = pathway.split("\t")[0]
                pathwayName = pathwayName[5:]
                # replace "map" by "hsa" (because we want the reference organisms for homo sapiens)
                pathwayName = pathwayName.replace("map", "hsa")

                pathway_resource = self.webservice.get(pathwayName, "kgml")
                #only read the pathway if it contains meaningful information
                if len(str(pathway_resource)) > 10:
                    if count <= int(self.config["maxNumPathways"]):
                        xmlPathway = self.webservice.parse_kgml_pathway(pathwayName, pathway_resource)
                        parsed_pathway = self.pathwayparser.parsePathway(xmlPathway, pathwayName)
                        #only add if the pathway is not empty
                        if parsed_pathway.vcount > 0:
                            pathway_graphs[pathwayName] = parsed_pathway
                            count += 1
                    else:
                        break

        return pathway_graphs


class Disgenet(KnowledgeBase):
    """Knowledge base implementation for DisGeNET.

       :param name: name of the knowledge base
       :type name: str
       :param config: configuration parameter of the knowledge base as specified in the config file.
       :type config: dict
       :param webservice: web service querying implementation.
       :type webservice: :class:`DISGENET`
       :param hasGeneInformation: true if the knowledge base provides gene association information, false otherwise
       :type hasGeneInformation: bool
       :param hasPathwayInformation: true if the knowledge base also provides pathway information, false otherwise
       :type hasPathwayInformation: bool
       """

    def __init__(self):
        super().__init__("DisGeNET", util.getConfig("DisGeNET"), DISGENET(), True, False)

    def getRelevantGenes(self, labels):
        """Get all genes that are related to a set of labels, e.g. disease names.

           :param labels: list of identifiers, e.g. disease names, for which to find associated genes.
           :type labels: list of str
           :return: list of associated genes.
           :rtype: list of str
           """

        assocs = self.webservice.query(labels)

        #check if error code was returned
        if isinstance(assocs, int):
            print("ERROR " + str(assocs) + " RETURNED FOR LABELS: " + ", ".join(labels))
            return pd.DataFrame(columns = ["gene_symbol", "score"])

        # extract only the genes from the results
        # for now, just merge all gene sets from the query into one (no matter how many genes were associated to a particular disease
        # (=no interleaving)
        relevantGenes = set(assocs.loc[:,"gene_symbol"])

        return list(relevantGenes)

    def getGeneScores(self, labels):
        """Get association scores for all genes that are related to the provided labels, e.g. disease names.
           DisGeNET provides a couple of association scores to its genes (https://www.disgenet.org/dbinfo).
           Which score to use can be defined by the user in the config file.

           :param labels: list of identifiers, e.g. disease names, for which to find associated genes.
           :type labels: list of str
           :return: DataFrame of associated genes and their association scores, in descending order.
           :rtype: :class:`pandas.DataFrame`
           """
        assocs = self.webservice.query(labels)
        # check if an error code was returned
        # check if error code was returned
        if isinstance(assocs, int):
            print("ERROR " + str(assocs) + " RETURNED FOR LABELS: " + ", ".join(labels))
            return pd.DataFrame(columns = ["gene_symbol", "score"])

        if assocs.empty:
            return pd.DataFrame(columns = ["gene_symbol", "score"])

        assocs.columns = ["gene_symbol", "score"]
        #sort by assoc score
        assocs.sort_values("score", inplace=True, ascending = False)
        # for duplicate gene entries, select entries with highest association score
        assocs.drop_duplicates("gene_symbol", keep="first")
        return assocs

    def getRelevantPathways(self, labels):
        """As DisGeNET currently does not provide pathway information, this feature is not implemented.

           :param labels: list of labels for which to find related pathways.
           :type labels: list of str
           :return: :class:`NotImplementedError` as this knowledge base is not intended to be used for such analyses.
           :rtype: :class:`NotImplementedError`
           """
        raise NotImplementedError("DisGeNET is not a pathway database. Querying for pathways is not possible.")


class Pathwaycommons(KnowledgeBase):
    """Knowledge base implementation for PathwayCommons.

       :param name: name of the knowledge base
       :type name: str
       :param config: configuration parameter of the knowledge base as specified in the config file.
       :type config: dict
       :param webservice: web service querying implementation.
       :type webservice: :class:`opentargets.OpenTargetsClient`
       :param hasGeneInformation: true if the knowledge base provides gene association information, false otherwise
       :type hasGeneInformation: bool
       :param hasPathwayInformation: true if the knowledge base also provides pathway information, false otherwise
       :type hasPathwayInformation: bool
       """
    def __init__(self):
        super().__init__("PathwayCommons", util.getConfig("PathwayCommons"), PATHWAYCOMMONSWS(), True, True)

    def getGeneScores(self, labels):
        """Get association scores for all genes that are related to the provided labels, e.g. disease names.
           For PathwayCommons, the association score for a gene is the sum of its degree percentile rank for every pathway, normalized by the overall number of pathways retrieved.
           This favors hub genes/genes having many interactions with other genes.

           :param labels: list of identifiers, e.g. disease names, for which to find associated genes.
           :type labels: list of str
           :return: DataFrame of associated genes and their association scores, in descending order.
           :rtype: :class:`pandas.DataFrame`
           """

        pathways = self.getRelevantPathways(labels)
        overallCount = len(pathways)
        occurrenceCounts = {}
        for pathway in pathways.values():
            nodes = pathway.nodes
            interactions = pathway.interactions_by_nodes
            reduced_interactions = {}
            # update interactions to only store the interactions counts
            for entity in interactions.keys():
                reduced_interactions[entity.label] = len(interactions[entity])
            # make dataframe from count
            interactions_df = pd.DataFrame.from_dict(reduced_interactions, orient='index')
            interactions_df.columns = ["degree"]
            percentiles = interactions_df["degree"].rank(method='min', pct=True)
            for item in percentiles.iteritems():
                perc_score = item[1]
                feature = item[0]
                if feature in occurrenceCounts.keys():
                    occurrenceCounts[feature] += perc_score
                else:
                    occurrenceCounts[feature] = perc_score

        genes = list()
        scores = list()
        for geneID in occurrenceCounts.keys():
            genes.append(geneID)
            score = occurrenceCounts[geneID] / overallCount
            scores.append(score)

        geneScores = pd.DataFrame({"gene_symbol": genes, "score": scores})
        geneScores.sort_values("score", inplace=True, ascending=False)

        return geneScores

    def getRelevantGenes(self, labels):
        """Get all genes that are related to a set of labels, e.g. disease names.
           For PathwayCommons, this means we retrieve all genes that are contained in pathways associated to these labels.

           :param labels: list of identifiers, e.g. disease names, for which to find associated genes.
           :type labels: list of str
           :return: list of associated genes.
           :rtype: list of str
           """
        pathways = self.getRelevantPathways(labels)
        genes = set()
        for pathway in pathways.values():
            nodes = pathway.nodes
            for node in nodes.values():
                genes.add(node.label)

        return genes

    def readPathway(self, pathway):
        """Reads a pathway to create :class:`pypath.Network`.

           :param pathway: pathway string to parse
           :type pathway: str
           """
        interactions = pathway.text.split("\n")
        for interaction in interactions:
            yield interaction.split()

    def getRelevantPathways(self, labels):
        """Get all pathways related to a set of labels, e.g. disease names as :class:`pypath.Network`.

           :param labels: list of gene names to be mapped
           :type labels: list of str
           :return: dict of pathway names and their internal representation as :class:`pypath.Network`.
           :rtype: dict
           """
        #collect pathway IDs first
        overall = 0
        pathways = {}
        p_ids = set()
        for term in labels:
            pathwayIDs = self.webservice.search(term, organism="homo sapiens", type="pathway")
            # if no error code was returned
            if (pathwayIDs is None) or isinstance(pathwayIDs, int):
                continue

            numHits = pathwayIDs["numHits"]
            maxHits = pathwayIDs["maxHitsPerPage"]
            pages = math.ceil(numHits / maxHits)
            if pages > 1:
                for i in range(0, pages):
                    pathwayIDs = self.webservice.search(term, page=i, organism="homo sapiens", type="pathway")

                    #if no error code was returned
                    if (pathwayIDs is None) or isinstance(pathwayIDs, int):
                        continue

                    items = pathwayIDs["searchHit"]
                    overall += len(items)
                    for item in items:
                        p_ids.add(item["uri"])



        count = 0
        for id in p_ids:
            pathway_sif = self.webservice.get(id, frmt = "SIF")
            #if server does not return an error code and the pathway has a sif version
            if (pathway_sif is None):
                continue

            if not isinstance(pathway_sif, int) and not (pathway_sif.text == ""):
                #only load the pathway if the maxNumPathways count is not reached yet
                if count <= int(self.config["maxNumPathways"]):
                    params = {"self": self, "pathway": pathway_sif}

                    #create pypath pathway from SIF
                    input = input_formats.NetworkInput(
                        name=id,
                        input= Pathwaycommons.readPathway,
                        input_args=params,
                        separator='\t',
                        id_col_a=0,
                        id_col_b=2,
                        id_type_a='genesymbol',
                        id_type_b='genesymbol',
                        sign = (1, "+", "-")
                    )

                    pathway = network.Network()
                    pathway.load(input)
                    #only add pathway if it has nodes
                    if pathway.vcount > 0:
                        pathways[id] = pathway
                        count += 1

                else:
                    break
            else:
                continue

        return pathways

############################### PATHWAY MAPPERS ###############################

class PathwayParser():
    """Super class that maps a pathway from its original format (provided by a knowledge base) to the internally used :class:`pypath.Network`.
       When having to map pathways from a knowledge base, implement a new class that inherits from this one and implements :meth:`PathwayParser.parsePathway()`.
       """

    #abstract method for pathway parsing. returns an igraph object for the input pathway
    @abstractmethod
    def parsePathway(self, pathway, pathwayID):
        """Abstract method.
           Parse a pathway to the internally used format of :class:`pypath.Network`.

           :param pathway: pathway string to parse
           :type pathway: str
           :param pathwayID: name of the pathway
           :type pathwayID: str
           :return: pathway in the internally used format..
           :rtype: :class:`pypath.Network`
           """
        pass

class KEGGPathwayParser(PathwayParser):
    """Parse KEGG pathways, which are returned in KGML format.
       """

    def readInteractions(self, interactions, geneIds):
        """Parses interactions for a set of genes.

           :param interactions: interactions to parse
           :type interactions: list
           :param geneIds: gene ids whose interactions to add
           :type geneIds: list of str
           """
        for interaction in interactions:
            # filter pathway relations for protein-protein (PPrel) and gene expression (GErel) interactions
            if (interaction["link"] == "PPrel") or (interaction["link"] == "GErel"):
                try:
                    source = geneIds[interaction["entry1"]].label
                    target = geneIds[interaction["entry2"]].label
                    relation_name = interaction["name"]
                    interactionString = "\t".join([source, target, relation_name])
                    yield interactionString.split()
                except:
                    continue

    def parsePathway(self, kgml_pathway, pathwayID):
        """Parse KEGG pathway to the internally used format of :class:`pypath.Network`.

           :param pathway: pathway string to parse
           :type pathway: str
           :param pathwayID: name of the pathway
           :type pathwayID: str
           :return: pathway in the internally used format..
           :rtype: :class:`pypath.Network`
           """

        #create gene IDs first
        geneIds = {}
        for entry in kgml_pathway["entries"]:
            if entry["type"] == "gene":
                # select first of the gene names in the list to be the alias
                node = entity.Entity(entry["gene_names"].split(", ")[0].strip("..."))
                geneIds[entry["id"]]= node

        params = {"self": self, "interactions": kgml_pathway["relations"], "geneIds": geneIds}

        # create pypath pathway from SIF
        input = input_formats.NetworkInput(
            name=pathwayID,
            input=KEGGPathwayParser.readInteractions,
            input_args=params,
            separator='\t',
            id_col_a=0,
            id_col_b=1,
            id_type_a='genesymbol',
            id_type_b='genesymbol',
            sign=(2, "+", "-")
        )

        pathway = network.Network()
        pathway.load(input)

        return pathway
