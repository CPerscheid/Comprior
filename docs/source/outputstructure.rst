.. _outputStructure:

Folder Structure  - Where to find what Files (In- and Output)
=============================================================

Unless the paths are not adapted/overwritten in *config.ini*, Comprior builds up the following folder infrastructure during processing:
::

  data
   ├── input
   │   ├── dataset
   │   └── example
   ├── intermediate
   │   ├── dataset
   │   ├── crossvalidation
   │   └── externalKnowledge
   └── results
       └── XXX
           ├── timeLogs
           ├── preanalysis
           ├── geneRankings
           └── evaluation
               ├── rankings
                   ├── annotation
                   └── metrics
               ├── reducedData
               └── classification
                   ├── metrics
                   └── crossEvaluation
                       ├── reducedData
                       └── classification



input/
*********

  * **dataset/**: put your input dataset here
  * **example/**: folder with example files for trying out Comprior

intermediate/
****************

  * **dataset/**: preprocessed input data (currently metadata added to one file)
  * **crossvalidation/**: contains preprocessed dataset for cross-validation (e.g. mapped to the right identifier or pathway features)
  * **externalKnowledge/**: one sub-folder per knowledge base that is queried with query results

results/
***********

  * **XXX/**: output folder for the current run, whose name is specified by the *outputDir_name* parameter in *config.ini* (if there already exists a folder with such a name, Comprior adds a number to the name)

    * **timeLogs/**: one file for every selected approach, containing logs with time durations of different selection activities, e.g. external knowledge retrieval or statistical feature selection
    * **preanalysis/**: contains - if selected via *preanalysis_plots* and *evaluateKBcoverage* parameters in *config.ini* - plots on data set characteristics and knowledge base coverage
    * **geneRankings/**: contains the actual feature rankings, one CSV file for every selected approach
    * **evaluation/**: contains all evaluation results

        * **rankings/**: contains evaluation results from analyzing the feature rankings

          * **annotation/**: contains annotation/enrichment files for every ranking
          * **metrics/**: contains the actual metrics results to compare the rankings

        * **reducedData/**: one sub-folder per selection approach containing input data for the top k features; these files are used for the actual classification/prediction
        * **classification/**:

          * **metrics/**: contains the actual classification metrics results, one CSV file for every selected metric, also contains pdfs for visualizations
          * **crossEvaluation/**: contains evaluation data from the second data set for cross-validation

            * **reducedData/**: one sub-folder per selection approach containing input data (second data set) for the top k features; these files are used for the actual classification/prediction
            * **classification/**: contains the actual classification metrics results, one CSV file for every selected metric, also contains pdfs for visualizations
