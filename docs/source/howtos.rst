Extending Comprior - How-Tos
============================

Add New Preprocessing Functionality
***********************************

1. Implement a new Preprocessor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Every preprocessing functionality must be implemented in its own class.
To achieve that, create a new class that inherits from :class:`preprocessing.Preprocessor` and implements :meth:`preprocessing.Preprocessor.preprocess` method, e.g.
::

  class ExamplePreprocessor(Preprocessor):
    """Does some example preprocessing

      :param input: absolute path to the input file to preprocess.
      :type input: str
      :param output: absolute path to the output directory where to store the preprocessing results.
      :type output: str
      :param whatever_you_need: whatever other parameters your preprocessor needs.
      """

    def __init__(self, input, output, whatever_you_need):
      self.whatever_you_need = whatever_you_need
      super().__init__(input, None, output)

    def preprocess(self):
      """Does some example preprocessing

         :return: absolute path to the new file location.
         :rtype: str
         """
      #implement your preprocessing here...

      return self.output

2. Update the Config File (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your preprocessing functionality requires that the user sets any specific parameters, adapt the preprocessing section of *config.ini* and include these parameters.
Do not forget to provide this config to your preprocessor class then.

3. Include the Preprocessor in the Execution Pipeline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Add your preprocessor to :meth:`pipeline.Pipeline.preprocessData` method.
Make sure that a) :class:`preprocessing.DataTransformationPreprocessor` is always the first preprocessor (it transforms the file to use pandas' default separator so that we do not need to handle different separators anymore), b) all preprocessores write their outputs to the same intermediate directory, and c) set the correct inputs: your preprocessor's input is the output of the preceding preprocessor, your preprocessor's output will be the input of the subsequent preprocessor:
::

  dataFormatter = preprocessing.DataTransformationPreprocessor(input, input_metadata, intermediate_output, sep)
  transposed_input = dataFormatter.preprocess()

  #here comes your new preprocessor
  examplePreprocessor = preprocessing.ExamplePreprocessor(transposed_input, intermediate_output, whatever_you_need)
  exampled_input = examplePreprocessor.preprocess()

  mappingPreprocessor = preprocessing.MappingPreprocessor(exampled_input, intermediate_output, currentIDFormat, desiredIDFormat, False)
  mapped_input = mappingPreprocessor.preprocess()

Add a New Knowledge Base
************************

Every knowledge base needs to classes: One class inheriting from :class:`knowledgebases.KnowledgeBase` and implementing the interface methods and a second class inheriting from bioservice's REST class for web service access.

1 Implement KnowledgeBase Class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The class inheriting from :class:`knowledgebase.KnowledgeBase` is accessed from any other class within Comprior that wants to retrieve prior knowledge.
It must implement the methods :meth:`knowledgebases.KnowledgeBase.getRelevantGenes`, :meth:`knowledgebases.KnowledgeBase.getGeneScores`, and :meth:`knowledgebases.KnowledgeBase.getRelevantPathways` (depending on the type of knowledge base, raise a NotImplementedError).

::

  class ExampleKB(KnowledgeBase):
    def __init__(self):
      #pass the knowledge base name, its config, the web service accessing class, and booleans indicating what type of knowledge is provided by that knowledge base
      geneInfo = True
      pathwayInfo = False
      super().__init__("ExampleKB", util.getConfig("ExampleKB"), ExampleKBWS(), geneInfo, pathwayInfo)

    def getRelevantGenes(self, labels):
      """Get all genes that are somehow associated to the given labels, e.g. disease names.

       :param labels: list of identifiers, e.g. disease names, for which to find associated genes.
       :type labels: list of str
       :return: list of associated genes.
       :rtype: list of str
       """

      #implement the gene retrieval strategy here...
      return genes


    def getGeneScores(self, labels):
    """Get all genes and their association scores that are related to the given labels, e.g. disease names.

         :param labels: list of identifiers, e.g. disease names, for which to find associated genes.
         :type labels: list of str
         :return: DataFrame of associated genes and their association scores, in descending order.
         :rtype: :class:`pandas.DataFrame`
         """

      #implement the gene score retrieval strategy here...
      #if your knowledge base provides pathways only, you can implement an own strategy or raise a NotImplementedError

      return geneScores

    def getRelevantPathways(self, labels):
      """As this knowledge base currently does not provide pathway information, this feature is not implemented.

         :param labels: list of labels for which to find related pathways.
         :type labels: list of str
         :return: :class:`NotImplementedError` as this knowledge base is not intended to be used for such analyses.
         :rtype: :class:`NotImplementedError`
         """

      #if the knowledge base does not provide pathway information, raise a NotImplementedError

      raise NotImplementedError()

2 Implement a Pathway Parser (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the knowledge base provides pathway or network information, parse the pathway information into a pypath :class:`pypath.Network` (for an example, see :class:`knowledgebases.KEGGPathwayParser`).
Inherit from :class:`knowledgebases.PathwayParser` to do that and implement your own :meth:`knowledgebases.PathwayParser.parsePathway` method:
::

  class ExamplePathwayParser(PathwayParser):
    """Parses a pathway from a custom format to :class:`pypath.Network`.
      """

    def parsePathway(self, pathway, pathwayID):
      """Parse pathway to the internally used format of :class:`pypath.Network`.

         :param pathway: pathway string to parse
         :type pathway: str
         :param pathwayID: name of the pathway
         :type pathwayID: str
         :return: pathway in the internally used format..
         :rtype: :class:`pypath.Network`
         """

      #implement your pathway parsing strategy here...

      return pathway

3 Implement Web Service Accessing Class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First of all, check if bioservices already provides a class for accessing the knowledge base web service: https://bioservices.readthedocs.io/en/master/references.html#services
If your knowledge base is not available, implement your own class by inheriting from bioservice's REST or WSDL classes.
Optimally, your REST class provides the API endpoints as methods, so if there is an endpoint *search*, implement a corresponding method named *search*.
To send the actual request, construct a query string that specifies our endpoint (without the general API url) and provide that string to *self.http_get(your_string)*.
::

  class ExampleKBWS(REST):
  """Queries the web service of ExampleKB for a given set of labels and retrieves association scores for all genes related to the query labels.
     """
  def __init__(self):
      super().__init__("ExampleKBWS", url=util.config["ExampleKB"]["webservice_url"])

  def getVersion(self):
      """Get the current version of the API endpoint.

         :return: web service version infos.
         :rtype: json dict
         """
      ret = self.http_get("/version")
      return ret

4 Update the Config File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create a new section in *config.ini* for your knowledge base.
It must contain an output directory (where intermediate results are written to), optionally the web service API URL (if you had to implement your own REST class), and any other parameter you need for your knowledge base class to function.
::

  [ExampleKB]
  webservice_url = https://www.myexamplekbwebservice.org/api
  outputDir = ${General:externalKbDir}ExampleKB/

5 Register the Knowledge Base at KnowledgeBaseFactory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Register your new knowledge base at :meth:`knowledgebases.KnowledgeBaseFactory.createKnowledgeBase`.
If your knowledge base is o not forget to provide the pathway parser to your knowledge base when creating
::

  def createKnowledgeBase(self, knowledgebase):
  """Creates knowledge base based on a given name.

   :param knowledgebase: name of the knowledge base to be created.
   :type knowledgebase: str
   :return: knowledge base object.
   :rtype: :class:`KnowledgeBase` or inheriting classes
   """

   if knowledgebase == "ExampleKB":
      return ExampleKB()

    if knowledgebase == "ExamplePathwayKB":
      #create a pathway parser if your knowledge base requires that
      pathwayparser = ExamplePathwayParser()
      return ExamplePathwayKB(pathwayparser)

Add a new Feature Selector Approach
************************************

1a. Implement a Feature Selector
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Feature selection approaches are implemented in separate classes for each approach.
Inherit from one (or multiple) of the many abstract classes that are available for feature selectors, e.g. :class:`featureselection.RSelector` when invoking R code or :class:`featureselection.PriorKnowledgeSelector` when implementing a prior knowledge approach that uses a knowledge base.
See all the class hierarchy HERE.
::

  class ExampleSelector(PriorKnowledgeSelector):
    def __init__(self, knowledgebase, whatever_you_need):
      self.whatever_you_need = whatever_you_need
      super().__init__("YourSelectorName", knowledgebase)

    def selectFeatures(self):
    """Your feature selection strategy.

      :return: absolute path to the output ranking file.
      :rtype: str
      """

      #define the name of the output file name (must follow this schema!)
      outputFilename = self.output + self.getName() + ".csv"

      #implement your feature selection procedure here...

      return outputFilename


1b. Implement a Network Selector
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you want to implement a network approach that maps the original feature space of the data to (sub-)networks, e.g. pathways, inherit from :class:`featureselection.NetworkSelector` and implement its :meth:`featureselection.NetworkSelector.selectPathways` instead:
::

  class ExampleNetworkSelector(NetworkSelector):

    def __init__(self, knowledgebase, featuremapper):
      super().__init__("YourNetworkSelector", knowledgebase, featuremapper)

    def selectPathways(self, pathways):
    """Your pathway selection strategy

      :param pathways: selector name
      :type pathways: str
      :returns: pathway ranking with pathway scores
      :rtype: :class:`pandas.DataFrame`
      """
      #implement your pathway/subnetwork selection strategy here...

      return pathwayRanking

Classes inheriting from :class:`featureselection.NetworkSelector` additionally require a feature mapper that, once the (sub-) networks were selected as new features by your new network selector, creates new feature values for every selected (sub-) network.
To do that, either use an existing feature mapper or implement a new one that inherits from :class:`featureselection.FeatureMapper` and implements :meth:`featureselection.FeatureMapper.mapFeatures`:
::

  class ExampleFeatureMapper(FeatureMapper):

          def __init__(self, ):
              super().__init__()

          def mapFeatures(self, original_data, subnetworkNames, subnetworks):
          """Your feature mapping strategy

            :param original_data: the original data set of which to map the feature space.
            :type original_data: :class:`pandas.DataFrame`
            :param pathways: dict of pathway names as keys and corresponding pathway :class:`pypath.Network` objects as values
            :type pathways: dict
            :returns: the transformed data set with new feature values
            :rtype: :class:`pandas.DataFrame`
            """
            #implement your feature mapping strategy here...

            return mappedDataset

2. Update the Config File
^^^^^^^^^^^^^^^^^^^^^^^^^

List the new feature selection approach in the comments of the *config.ini* file and preferably, this Wiki ;).
When providing a name to your feature selection approach, follow this naming schema (*YourSelectorName* MUST be the same as the name provided in the selector's init method):

* *YourSelectorName* for a traditional approach without any knowledge base
* *YourSelectorName_kbName* for a selector that uses a knowledge base
* *YourSelectorName_tradName_kbName* for a selector that uses a knowledge base and another selector.

3. Register Feature/Network Selection Approach to the FeatureSelectorFactory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Register your new feature selector class at :class:`featureselection.FeatureSelectorFactory` in one of the following methods, depending on the type of selector you implemented (see the sources as the methods are encapsulated in a singleton construct):

* :meth:`featureselection.FeatureSelectorFactory.createTraditionalSelector` if it is a traditional selector not using a knowledge base
* :meth:`featureselection.FeatureSelectorFactory.createCombinedSelector` if it uses a traditional approach and a knowledge base in a combined manner
* :meth:`featureselection.FeatureSelectorFactory.createIntegrativeSelector` if it is a selector that only uses a knowledge base

When registering, you need to specify the first part (=YourSelectorName) of the overall name as an if-statement
::

  def createIntegrativeSelector(self, selectorName, kb):
  """Creates a feature selector using a knowledge base from the given selector and knowledge base names.
    Register new implementations of a prior knowledge selector here that does not requires a (traditional) selector.
    Stops processing if the selector could not be found.

    :param selectorName: selector name
    :type selectorName: str
    :param kb: knowledge base name
    :type kb: str
    :return: instance of a feature selector implementation.
    :rtype: :class:`FeatureSelector` or inheriting class
    """
    kbfactory = knowledgebases.KnowledgeBaseFactory()
    knowledgebase = kbfactory.createKnowledgeBase(kb)

    if selectorName == "YourSelectorName":
      return ExampleSelector(knowledgebase)

    if selectorName == "YourNetworkSelectorName":
        featureMapper = ExampleFeatureMapper()
        return ExampleNetworkSelector(knowledgebase, featureMapper)



Add Custom Code from R/Java/another Programming Languages
*************************************************************

.. _invokingRjavacode:

Invoking R or Java Code
^^^^^^^^^^^^^^^^^^^^^^^
  The benchutils package provides methods for invoking R or Java code (:meth:`benchutils.runRCommand` and :meth:`benchutils.runJavaCommand`, respectively).
  These methods are already used, e.g. by :meth:`featureselection.RSelector.selectFeatures` and :meth:`featureselection.JavaSelector.selectFeatures`.
  If you have R or Java code that you want to invoke, use these methods and provide them with the R/Java config parameters, the name of the script/jar to execute, and a list of parameters.
  The example below runs an R script called "FS_LassoPenalty.R" that expects three parameters providing file names to the input, output, and external score files.
  ::

    params = [input_filename, output_filename, externalscores_filename]
    benchutils.runRCommand(self.rConfig, "FS_LassoPenalty.R" , params)

Invoking Code from Another Programming Language than R or Java
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  Currently, Comprior supports to run Python, R, and Java code.
  If you want to integrate custom code from another programming language, you can implement a corresponding function like :meth:`benchutils.runRCommand` and :meth:`benchutils.runJavaCommand`.
  Such a function constructs an execution string that is then forwarded to the command line.
  To do that,

    * create a new folder for your programming language in Comprior's *code* directory (next to the *Python*, *R*, and *Java* directories), e.g. *Cpp* for adding C++ code
    * place your executable files or script(s) into the new directory
    * adapt the *config.ini* file and add a new segment for the programming language that contains the path to your executable source code (e.g. the *compiled* files of your C++ code) and to the programming language interpreter (for C++, however, code is invoked by just typing *./filename* on the command line)

    ::

      [C++]
      code = ${General:homePath}code/Cpp
      CppLocation=./


    * adapt *benchutils.py* and implement an additional function (do not forget to add code documentation!)

    ::

      def runCppCommand(cppConfig, filename, params):
      """Run external C++ code.

        :param cppConfig: C++ config parameters (store paths to C++ and the C++ code).
        :type cppConfig: dict
        :param filename: name of the C++ file to be executed.
        :type filename: str
        :param params: list of parameters that will be forwarded to the C++ file.
        :type params: list of str
        """
        args = [cppConfig["C++"], filename]
        args.extend(params)
        print(args)
        p = subprocess.Popen(args, cwd=cppConfig["code"])
        p.wait()

    * invoke your code from within Python as described above in :ref:`invokingRjavacode`.
