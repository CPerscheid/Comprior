Input Data Sets
=============================

Gene Expression Data
********************

The gene expression dataset must be provided in table format.
Genes/features can be located either in columns or rows, however make sure to set the *genesInColumns* parameter accordingly in your config file.
Data separators can be chosen arbitrarily, however make sure to set the *dataSeparator* parameter accordingly.
**Make sure to always leave the first column of the header empty as shown here**:

+-----------------------------------------+
|  ,ERBB2,TP53,DVL1,BRCA1,BRCA2           |
+=========================================+
| **Sample1**,12.02,4.12,11.25,9.87,10.02 |
+-----------------------------------------+
| **Sample2**,10.32,4.76,10.73,10.94,8.72 |
+-----------------------------------------+

Metadata
**********

Metadata must always be provided for an input data set.
It must have the same separator as the gene expression data (pay attention: here you do not have to leave a blank column).
Whether samples or metadata type is located in the columns can be specified with the *metadataIDsInColumns* parameter.
Specify the class labels by selecting a corresponding metadata type with the *classLabelName* parameter (e.g. if we want to have subtypes as class labels, specify *subtype*).
If the metadata provides further information on the disease that you want to provide as search terms for the knowledge bases, specify it with the *diseaseLabelName* parameter (e.g. by setting it to *primary_diagnosis*).

+-----------------------------------------------------------------------------------+
| Sample1,Sample2                                                                   |
+===================================================================================+
| **project_id**,BRCA,BRCA                                                          |
+-----------------------------------------------------------------------------------+
| **subtype**,LumA,LumB                                                             |
+-----------------------------------------------------------------------------------+
| **gender**,female,female                                                          |
+-----------------------------------------------------------------------------------+
| **primary_diagnosis**,"Infiltrating duct carcinoma, NOS","Lobular carcinoma, NOS" |
+-----------------------------------------------------------------------------------+

Data for Cross-Validation
*************************

Preprocessing for data sets for cross-validation is currently not supported (except for identifier mapping), so the data must be provided with a) genes in columns and b) the corresponding class labels.
Make sure to set the name of the class label column in the config file with the *crossEvaluationClassLabel* parameter (in the example, it would be *diseaseCode*).

+-----------------------------------------------------+
|  diseaseCode,SampleName,ERBB2,TP53,DVL1,BRCA1,BRCA2 |
+=====================================================+
| **LumA,Sample1**,12.02,4.12,11.25,9.87,10.02        |
+-----------------------------------------------------+
| **LumB,Sample2**,10.32,4.76,10.73,10.94,8.72        |
+-----------------------------------------------------+
