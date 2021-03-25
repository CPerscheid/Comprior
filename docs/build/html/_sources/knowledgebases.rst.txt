Knowledge Bases
================

* Comprior queries a knowledge base to retrieve relevant genes, gene association scores, or pathway information, which is then integrated into a prior knowledge feature selection approach
* for the search, Comprior uses a) the class labels and b) alternative search terms that are provided in the config file (see *alternative search terms* parameter in configuration specification)

`DisGeNET <https://www.disgenet.org/>`_
*****************************************

* aggregates biological information from multiple sources (meta knowledge base, see `sources description <https://www.disgenet.org/dbinfo>`_ for original sources)
* provides gene-disease, variant-disease, and variant-gene association scores for genes, disease, and variants (no pathway information) --> used for retrieving relevant genes and gene association scores
* users can choose in the config whether to use DisGeNET's gene-disease association (GDA) score, disease pleiotropy index, or disease specificity index (see `their description <https://www.disgenet.org/dbinfo>`_ for more information)
* DisGeNET uses UMLS identifiers for the search, so Comprior internally first maps the search terms to their corresponding UMLS CUI (via the `UMLS terminology web service <https://uts.nlm.nih.gov/uts/>`_) and forwards these to DisGeNET



`OpenTargets <https://www.targetvalidation.org/>`_
****************************************************

* provides biological information from multiple sources (meta knowledge base, see `their documentation <https://docs.targetvalidation.org/data-sources/data-sources>`_ for original sources)
* provides association gene-disease association scores (no pathway information) --> used for retrieving relevant genes and gene association scores

`KEGG <https://www.kegg.jp/>`_
********************************

* provides manually curated pathway information --> used for retrieving relevant genes, gene association scores, and pathway information
* pathways are parsed into pypath.Network format

Retrieving Relevant Genes from Pathway Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Comprior retrieves relevant genes from a set of pathways by selecting all their member genes and removing duplications


Gene Association Score Computation from Network Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Comprior computes a gene association score :math:`s_i` for a gene :math:`i` from the sum of its degree percentile rank :math:`pr_i` for every pathway (= pathway genes are ranked by their number of in- and outgoing edges), normalized by the overall number of pathways retrieved: :math:`\frac{\sum_{n=1}^{|P|} pr_{n,i} if i \in p_n}{|P|}`
* this way, hub genes with a lot of interactions receive a higher score than genes at the outside rim of a pathway, becoming even more important if they have many interactions across multiple pathways

`PathwayCommons <http://www.pathwaycommons.org/>`_
***************************************************

* provides pathway information from multiple sources (meta knowledge base, see `their sources <http://www.pathwaycommons.org/>`_ for original sources)
* relevant genes and gene association scores are currently retrieved the same way as KEGG
* pathways are parsed into pypath.Network format
