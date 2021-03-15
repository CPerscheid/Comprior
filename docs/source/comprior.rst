Python Code Documentation
============================

pipeline module
---------------------
The framework module is responsible for orchestrating the complete benchmarking process.
It is the starting point that is invoked when running Comprior.
It tidies up and prepares working directories, creates and coordinates the execution order of preprocessing modules, feature selectors, and evaluation procedures.

.. automodule:: pipeline
    :members:
    :undoc-members:
    :show-inheritance:

benchutils module
---------------------
Utility module that provides functionality that is repeatedly used across the system, e.g. directory handling and file loading, identifier mapping, logging, and running external code from R or Java.
It also loads and stores the configuration parameters.

.. automodule:: benchutils
    :members:
    :undoc-members:
    :show-inheritance:
    :private-members:

preprocessing module
-------------------------
Contains all classes related to preprocessing.
All classes providing preprocessing functionality have to inherit from the abstract class :class:`preprocessing.Preprocessor` and implement its :meth:`preprocessing.Preprocessor.preprocess()` method.
For a detailed look at the class architecture, have a look at ADD CLASS ARCHITECTURE LINK HERE.

.. automodule:: preprocessing
    :members:
    :undoc-members:
    :show-inheritance:

featureselection module
----------------------------
Contains all classes related to feature selection.
Each feature selection approach must be implemented in its own class inheriting from the abstract super class :class:`featureselection.FeatureSelector` or one of its abstract subclasses, e.g. for including R or Java code.
Each feature selection class must implement setParams() and selectFeatures(), as input or output parameters are just set at runtime.

Feature extraction methods are implemented in the same structure, except that they need to have an instance of a class inheriting from :class:`featureselection.PathwayMapper` assigned to them so that the feature space can be transformed from the original to the new, e.g. pathways.

The creation of feature selectors is encapsulated by the class :class:`featureselection.FeatureSelectorFactory` that takes care that every selector is equipped correspondingly, e.g. with a knowledge base or another feature selector.
For a detailed look at the class architecture and the inheritance structure, have a look at ADD CLASS ARCHITECTURE LINK HERE.

.. automodule:: featureselection
    :members:
    :undoc-members:
    :show-inheritance:

knowledgebases module
--------------------------
Contains all classes related to knowledge bases.
A knowledge base is realized with two classes:
* A class inheriting from :class:`knowledgebases.KnowledgeBase` and implementing the three interface methods :meth:`knowledgebases.KnowledgeBase:getRelevantGenes`, :meth:`knowledgebases.KnowledgeBase:getGeneScores`, and :meth:`knowledgebases.KnowledgeBase:getRelevantPathways`.
* A class that is responsible for querying the corresponding web service and inherits from Bioservice's REST class.
Those knowledge bases that retrieve pathway information also need an additional PathwayMapper class, which transforms the original pathway results from the knowledge base (which can range from SIF to any other pathway specification format) into the pathway representation that is used throughout Comprior.
For Comprior's internal pathway representation, we use pypath.

The creation of knowledge bases is encapsulated by the class :class:`knowledgebase.KnowledgeBaseFactory` that takes care that every knowledge base is equipped with a web service querying class and, if needed, the right type of :class:`knowledgebase.PathwayMapper`.
For a detailed look at the class architecture, have a look at ADD CLASS ARCHITECTURE LINK HERE.

.. automodule:: knowledgebases
    :members:
    :undoc-members:
    :show-inheritance:

evaluation module
----------------------
Contains all classes related to the evaluation part.
There are distinct classes for the following evaluation aspects:
* review of knowledge base coverage for the provided search terms (see :class:`evaluation.KnowledgeBaseEvaluator`)
* inspection of data set quality, e.g. via mds or density plots (see :class:`evaluation.DatasetEvaluator`)
* comparison and assessment of feature rankings, e.g. overlap (see :class:`evaluation.RankingsEvaluator`)
* annotation of feature rankings and enrichment via EnrichR (see :class:`evaluation.AnnotationEvaluator`)
* classification and subsequent visualization of standard metrics (see :class:`evaluation.ClassificationEvaluator`)
* cross-classification across a second data set and visualization of standard metrics (see :class:`evaluation.CrossEvaluator`)

Every one of these classes inherits from the abstract :class:`evaluation.Evaluator` and implements the evaluate() method.
:class:`evaluation.AttributeRemover` is used in the overall benchmarking process to prepare the input data to contain only the selected features.
For a detailed look at the class architecture, have a look at ADD CLASS ARCHITECTURE LINK HERE.

.. automodule:: evaluation
    :members:
    :undoc-members:
    :show-inheritance:
