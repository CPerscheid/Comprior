Prior Knowledge Approaches
===============================

* Comprior provides multiple prior knowledge approaches of types :ref:`modifying`, :ref:`combining`, :ref:`network` as defined by Perscheid: `"Integrative biomarker detection on high-dimensional gene expression data sets: a survey on prior knowledge approaches" <https://academic.oup.com/bib/advance-article/doi/10.1093/bib/bbaa151/5881664?casa_token=hxOBxbrIx9sAAAAA:3z1uPc75bgQB2JRnWxsGhTFSSFeRSNB-Cuys4NAvI2sHcTXvcefH8fM5sNh9L66HFy9xXM5WOxQNmw>`_
* all of them can be flexibly combined with any of the available knowledge bases (see the configuration parameter description on how to do that)

.. _modifying:

Modifying Prior Knowledge Approaches
************************************

* type of prior knowledge used: list of relevant genes (no association scores)
* traditional feature selection and prior knowledge retrieval are carried out independently
* Comprior allows to design flexible modifying prior knowledge approaches that can be combined with any knowledge base and any traditional approach
* kind of two-level approaches that introduce an additional filtering or extension step before or after a traditional feature selection approach

Filtering
^^^^^^^^^^^^^^^

* *Prefilter*: prior knowledge is retrieved first and the input data set is filtered for those genes that were retrieved from the knowledge base; traditional feature selection is carried out afterwards
* *Postfilter*: Traditional feature selection is carried out first, and the resulting features are then filtered to keep only those that were also retrieved by the knowledge base
* prefilter and postfilter approaches have the same results for univariate feature selection approaches, e.g. Variance

Extension
^^^^^^^^^^^

* Comprior retrieves relevant genes and interleaves the gene ranking retrieved by a traditional approach with the set of relevant genes from the knowledge base
* this way, a feature set always not only contains traditionally selected genes, but also nearly as much genes that were retrieved from a knowledge base so that the feature set can contain genes that have a high statistical relevance but no (so far identified) biological relevance according to the knowledge base and vice versa

.. _combining:

Combining Approaches
**********************************

* type of prior knowledge used: relevant genes and their association scores (for the search terms)
* traditional feature selection and prior knowledge retrieval are carried out in parallel and integrated more thoroughly
* if a gene has multiple association scores (because it is associated to multiple search terms), Comprior will always keep the highest association score and remove the duplicate entries
* potentially, network information can also be retrieved via Comprior and then be mapped to some kind of relevance score, e.g. by incorporating topological information of a gene

LassoPenalty
^^^^^^^^^^^^^^

* gene association scores are used as individual penalty term per feature applied to Lasso
* Comprior uses the `xtune R package implementation <https://cran.r-project.org/web/packages/xtune/index.html>`_ by Zeng et al.: `"Incorporating prior knowledge into regularized regression" <https://pubmed.ncbi.nlm.nih.gov/32915960/>`_


WeightedScore
^^^^^^^^^^^^^^

* the final relevance score :math:`s_i` for a gene :math:`i` is made up of two parts: the association score from the knowledge base :math:`s_{i,kb}`, and the statistical relevance score :math:`s_{i,trad}` from a traditional approach
* both scores are equally weighted to compute the final relevance score for a gene: :math:`s_i = s_{i,kb} \times s_{i,trad}`

.. _network:

Network/Pathway Approaches
**************************

* network/pathway approaches use network information to identify (sub-) networks or pathways as new features and map the feature space from the original genes to the (sub-)networks
* network/pathway approaches thus always have a) a feature, i.e. pathway/subnetwork, selection step and b) a mapping step where new feature values must be computed

.. _networkactivity:

NetworkActivity
^^^^^^^^^^^^^^^^

* feature selection as described by Tian et al.: `"Discovering statistically significant pathways in expression profiling studies" <https://www.pnas.org/content/102/38/13544.short>`_

    *  a pathway/subnetwork is considered relevant if the gene expression profiles of its member genes correlate with the data set classes
    * average ANOVA score from all pathway member genes and class labels
    * rank pathways (= new features) by their ANOVA scores

* feature mapping is based on Vert and Kanehisa's definition of pathway relevance and smoothness: `"Graph-driven feature extraction from microarray data using diffusion kernels and kernel CCA" <http://members.cbio.mines-paristech.fr/~jvert/svn/bibli/local/Vert2003Graph-driven.pdf>`_

    * omputes pathway activity scores for every sample and pathway as new feature values.
    * the feature value :math:`v_{p,s}` for a pathway :math:`p`and sample :math:`s` is computed by taking the expression levels of all member genes :math:`i` (:math:`expr_i`) and weighting these by the variance :math:`var_i` of gene :math:`i` and the average correlation score :math:`corr_{i,neighbors_i}` of its neighbor genes in pathway :math:`p`: :math:`average(expr_i \times var_i \times corr_{i,neighbors_i})`

CorgsNetworkActivity
^^^^^^^^^^^^^^^^^^^^^^

* feature selection as described by :ref:`networkactivity`
* feature mapping as described by Lee et al: `"Inferring pathway activity toward precise disease classification" <https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000217>`_
    * the feature value :math:`v_{p,s}` for a pathway :math:`p` and sample :math:`s` is computed in the following way:

        * find the subset of genes (=CORGs) for which the score :math:`S(CORGs)` is maximal (via greedy search)
        * :math:`S(CORGs)` comes from a t-test between an activity vector :math:`a= (a_1, ..., a_n)` and class vector :math:`c = (c_1, ... c_n)` with :math:`n = \#samples`, i.e. every sample :math:`i` gets an activity score :math:`a_i` for the particular set of genes, :math:`c_i` is the class label of that sample
        * :math:`a_i` is computed from :math:`\frac{average(expr_{i,CORGs})}{\sqrt{k}}`, with :math:`k = \#CORGs` and :math:`expr_{i,CORGs}` being the expression values of all CORGs genes for sample :math:`i`
