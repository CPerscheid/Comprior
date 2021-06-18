.. _inputParams:

Configuration Parameters
************************

Config parameters are grouped into sections and needed by the framework to function properly.
In the following, we provide brief explanations for the existing parameters and their values

General
#######
* **name** - framework name, mainly used for logging
* **numCores** (*int*) - number of available cores that can be used for parallel running of gene selectors
* **homePath** - contains the path to the framework
* **inputDir** - the path to the directory where all input data is located
* **intermediateDir** - where to put intermediate results (recommended not to changed)
* **externalKbDir** - where to put intermediate query results from knowledge bases (recommended not to changed)
* **resultsDir** - where to put the final results (recommended not to changed)
* **preprocessing** - where to put preprocessed data sets (recommended not to changed)
* **crossVal_preprocessing** - where to put preprocessed data sets for cross-validation (recommended not to changed)
* **outputDir_name** - name of the overall output directory. If that directory already exists, Comprior adds numbering.
* **log_filename** - name of the log file to which processing information, warnings, etc. are written

R
##
* **code** - path to R source files (recommended not to changed)
* **RscriptLocation** - path to Rscript

Java
####
* **code** - path to Java jar files (recommended not to changed)
* **JavaLocation** - path to Java

Dataset
#######
* **input** - path to expression dataset
* **metadata** - path to metadata file for expression dataset
* **classLabelName** - specify the metadata column name of the label to use for classification (=keywords that will also be used for search in knowledge bases)
* **alternativeSearchTerms** - specify alternative search terms that will be used by knowledge bases. Separate search terms by spaces and replace spaces within a search term with _, e.g. "Breast Cancer Kidney_Cancer" will be parsed to the following search terms:"Breast", "Cancer", "Kidney Cancer"
* **genesInColumns** (*true/false*) - specify if genes are in the columns so that the data can be transformed automatically
* **metadataIDsInColumns** (*true/false*) - specify if sample IDs in the metadata file are in the columns
* **dataSeparator** (*sep*) - specify file separator (must be the same for metadata and gene expression), e.g. *,*, *\t*
* **currentGeneIDFormat** - specify the current gene ID format with g:Convert IDs, e.g. *ENTREZGENE, ENSG, AFFY_HG_U133_PLUS_2, HGNC* (see https://biit.cs.ut.ee/gprofiler/convert)
* **finalGeneIDFormat** - specify the gene ID format with g:Convert IDs you want to have in your gene rankings, e.g. *HGNC* (see https://biit.cs.ut.ee/gprofiler/convert)

Preprocessing
#############
* **filterMissingsInGenes** (*true/false*) - filter genes that have a higher percentage of missing fields than specified in treshold parameter
* **filterMissingsInSamples** (*true/false*) - filter samples that have a higher percentage of missing fields than specified in the treshold parameter
* **threshold** (*[0..100]*) - percentage used for filtering

Gene Selection - General
########################
* **outputDirectory** - where the final gene rankings are stored (recommended not to changed)
* **selectKgenes** (*int*) - maximum number of genes to select (to reduce runtimes). Must be >= topKmax param in  :ref:`evaluation`.


Gene Selection - Methods
########################
* **traditional_methods** - select multiple traditional gene selection methods (separated by spaces):

    * filter: *Random*, *InfoGain*, *ReliefF*, *VB-FS* (R-based variance selection), *ANOVA*, *mRMR*, *Variance* (Python-based variance selection)
    * wrapper: *SVMpRFE* (SVM-RFE with polykernel), *x-SFS*, *x-RFE* (x = add the desired classifier: K-nearest Neighbor (KNN3, KNN5), Naive Bayes (NB), Linear Regression (LR), Support Vector Machines with linear kernel (SVMl))
    * embedded: *RandomForest*, *Lasso*

* **modifying_methods** - combine knowledge base with traditional approach from above. Currently implemented:

    * *Postfilter_trad_kb*: Filter the features selected by traditional approach (*trad*) by the features/genes retrieved from knowledge base (*kb*)
    * *Prefilter_trad_kb*: Filter the input features by the genes retrieved from the knowledge base (*kb*) first and forward this reduced input set to the traditional approach (*trad*) for feature selection
    * *Extension_trad_kb*: Extends features selected by traditional approach (*trad*) by features/genes retrieved from knowledge base (*kb*). Traditionally selected features and external features/genes make up 50% of top k features, respectively (so if topKmax param is 2, 1 feature from traditional approach, 1 feature from external will be selected)
    * *KBonly_kb*: Only use the scores from the knowledge base to rank features, setting a default score of 0.000001.

* **combining_methods** - select combining methods to apply. Combining methods should combine a traditional approach (*trad*) with a knowledge base (*kb*), the prefix indicates the actual combining strategy. Currently implemented:

    * *Weighted_trad_kb*: weights the score from traditional approach *trad* by the score retrieved from knowledge base *kb*)
    * *LassoPenalty_kb*: includes external knowledge via Lasso penalty as described by Zeng et al.: `"Incorporating prior knowledge into regularized regression" <https://doi.org/10.1093/bioinformatics/btaa776>`_

* **network_methods** - select network approaches to apply. Currently implemented:

    * *NetworkActivity_kb*: retrieves pathway from knowledge base *kb*, ranks them via average of (ANOVA of gene expression value/sample class) for every gene in pathway, and creates an activity score as new feature value for the pathway for every sample (= average of (gene expression value x variance x average of (Pearson correlation with network neighbors))) for all genes in the pathway)
    * *CorgsNetworkActivity_kb*: retrieves pathway from knowledge base *kb*, ranks them via average of (ANOVA of gene expression value/sample class) for every gene in pathway, and creates an activity score as new feature value for the pathway for every sample as described by Lee et al.: `"Inferring Pathway Activity toward Precise Disease Classification" <https://doi.org/10.1371/journal.pcbi.1000217>`_

.. _evaluation:

Evaluation
###########
* **topKmin** (*int*) - minimum number of features to select
* **topKmax** (*int*) - maximum number of features to select
* **kfold** (*int*) - k parameter for k-fold cross-validation during classification
* **results** - where to put the results (recommended not to changed)
* **reducedDataset** - where to put the reduced data sets (with k features) (recommended not to changed)
* **preanalysis** - where to put plots created during preanalysis
* **preanalysis_plots** - create plots on input data before any analysis. Currently implemented:

    * *density*: density plot showing the average density distribution of expression values (per class)
    * *box*: box plot showing the average gene expression (per class)
    * *mds*: multidimensional scaling plot showing dis-/similarities between samples

* **evaluateKBcoverage** (*true/false*) - create diagrams showing coverage of search terms in the used knowledge bases
* **robustnessResults** - where to put the cross-validation results (recommended not to changed)
* **enableCrossEvaluation** (*true/false*) - whether to use a second data set for cross-validation
* **crossEvaluationData** - path to second data set for cross-validation (must have genes in columns and be already labeled)
* **crossEvaluationClassLabel** - column name of second data set for cross-validation containing the class label
* **crossEvaluationGeneIDFormat** - current g:Convert gene ID format of the second data set for cross-validation (see https://biit.cs.ut.ee/gprofiler/convert)
* **enableClassification** (*true/false*) - use classification algorithms for evaluation
* **enablePrediction** (*true/false*) - use predictive algorithms for evaluation (functionality not implemented yet)

Rankings
#########
* **results** - where to put the actual rankings (recommended not to change)
* **metricsDir** - where to put the metric results (recommended not to change)
* **annotationsDir** - where to put the annotation information(recommended not to change)
* **metrics** - specify which evaluation metrics to apply/compare on feature rankings. Currently provided:

    * *top_k_overlap*: overlap of top k features of rankings
    * *kendall_w*: Kendall's W ranking comparison
    * *fleiss_kappa*: Fleiss' Kappa ranking comparison
    * *annotation_overlap*: shows gene annotation overlap in rankings (e.g. which annotated genes where found jointly by all rankings)
    * *enrichment_overlap*: shows enrichment term overlap of rankings (e.g. which enrichment terms where found jointly by all rankings)
    * *annotation_percentage*: compares average p
    * *average_foldchange*: compares average fold change of genes in rankings

Classification
###############
* **classifiers** - specify classifiers to use for classsification task. Currently provided:

    * *KNN(int)*:  K-nearest Neighbor, e.g. *KNN3*
    * *NB*: Naive Bayes
    * *LR*: Linear Regression
    * *SMO*: Support Vector Machines
    * *RF*: Random Forest

* **metrics** - specify which evaluation metrics to apply on classification results. Currently provided:

    * *accuracy*
    * *sensitivity*
    * *specificity*
    * *F1*
    * *kappa*
    * *AUROC*
    * *precision*
    * *matthewcoef*: Matthews Correlation Coefficient

* **results** - where to put the classification results (recommended not to change)
* **crossEvaluationDir** - where to put classification results from cross-validation (recommended not to change)
* **metricsDir** - where to put the evaluation results (recommended not to change)

Prediction (not implemented yet)
########################################
* **predictors** - specify predictors to use for prediction task (still under construction)
* **metrics** - specify which evaluation metrics to apply on prediction results (still under construction)
* **results** - where to put the classification results (recommended not to change)
* **crossEvaluationDir** - where to put classification results from cross-validation (recommended not to change)
* **metricsDir** - where to put the evaluation results (recommended not to change)

Enrichr
#######
* **webservice_uri** - URL of Enrichr web service (recommended not to change)
* **outputDir**  - output directory for intermediate results from web service (recommended not to change)
* **geneSetLibrary** - gene set library to use for annotation/enrichment. Choose any available at https://maayanlab.cloud/Enrichr/#stats

OpenTargets
###########
* **outputDir**  - output directory for intermediate results from web service (recommended not to change)

KEGG
####
* **outputDir**  - output directory for intermediate results from web service (recommended not to change)
* **maxNumPathways** (*int*) - specify the maximum number of pathways to retrieve per search term (for performance reasons)

UMLS (needed to transform search terms into CUIs for using DisGeNET)
####################################################################################
* **login_uri** - URL of login web service (recommended not to change)
* **loginservice_uri** - URL of login web service (recommended not to change)
* **auth_endpoint** - authentication endpoint for API (recommended not to change)
* **apikey** - API key for accessing UMLS (recommended not to change unless own API key available, register for free at `UMLS <https://uts.nlm.nih.gov/uts/signup-login>`_ to create an own key)
* **webservice_uri** - URL of UMLS web service (recommended not to change)

DisGeNET
########
* **associationScore** (*score/gene_dsi/gene_dpi*) - which association score to use for knowledge retrieval: score (overall score), gene_dsi (disease specificity), gene_dpi (disease pleiotropy)
* **webservice_url** - URL of DisGeNET web service (recommended not to change)
* **outputDir** - output directory for intermediate results from web service (recommended not to change)
* **apikey** - API key for accessing DisGeNET (recommended not to change unless own API key is available, register at `DisGeNET <https://www.disgenet.org/signup/>`_ to create your own key)

PathwayCommons
##############
* **webservice_url** - URL of PathwayCommons web service (recommended not to change)
* **outputDir** - output directory for intermediate results from web service (recommended not to change)
* **maxNumPathways** (*int*) - specify the maximum number of pathways to retrieve per search term (for performance reasons)

BiomaRt
########
* **outputDir** - output directory for intermediate results from web service (recommended not to change)

gConvert
########
* **webservice_url** - URL of g:Convert web service (recommended not to change)
* **outputDir** - output directory for intermediate results from web service (recommended not to change)
