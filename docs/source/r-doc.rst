R Code Documentation
========================

Feature Selection
-----------------

.. rst:directive:: FS_mRMR.R

    .. raw:: html

      <details>
      <summary style="color:green;"><font size="-1">[sources]</font></summary>

    .. literalinclude:: ../../code/R/FS_mRMR.R
      :language: R

    .. raw:: html

      </details>

    Runs mRMR feature selection in parallel as implemented in the mRMRe package: De Jay, N. et al. "mRMRe: an R package for parallelized mRMR ensemble feature selection." Bioinformatics (2013).
    Although run in parallel, the performance is still not very good for high-dimensional data sets (>20.000    features).
    The resulting scores sometimes seem to not be sorted.
    However, these scores are the individual features' scores and feature combinations can result in a different overall ranking.
    Invoked by :class:`featureselection.MRMRSelector`.

    :param args: the input parameters parsed from the command line, consisting of a) the absolute path to the input data set file, b) the absolute path to the output file where the ranking will be stored, and c)the maximum number of features to select.

.. rst:directive:: FS_LassoPenalty.R

    .. raw:: html

      <details>
      <summary style="color:green;"><font size="-1">[sources]</font></summary>

    .. literalinclude:: ../../code/R/FS_LassoPenalty.R
      :language: R

    .. raw:: html

      </details>

    Runs Lasso feature selection with individual penalty scores for each feature as implemented in the xtune package: Zeng, C. et al.: "Incorporating prior knowledge into regularized regression", Bioinformatics (2020), https://doi.org/10.1093/bioinformatics/btaa776
    Invoked by :class:`featureselection.LassoPenaltySelector`.

    :param args: the input parameters parsed from the command line, consisting of a) the absolute path to the input data set file, b) the absolute path to the output file where the ranking will be stored, and c) the absolute path to the input ranking file (where the external rankings that will serve as penalty scores are stored).

.. rst:directive:: FS_Variance.R

    .. raw:: html

      <details>
      <summary style="color:green;"><font size="-1">[sources]</font></summary>

    .. literalinclude:: ../../code/R/FS_Variance.R
      :language: R

    .. raw:: html

      </details>

    Runs variance-based feature selection as implemented in the genefilter package.
    For every feature, computes its variance across all samples.
    Features are then ranked in descending order - highly variant features are more likely to separate samples into classes and seem to be the most interesting ones.
    Invoked by :class:`featureselection.VarianceSelector`.

    :param args: the input parameters parsed from the command line, consisting of ab) the absolute path to the input data set file and b) the absolute path to the output file where the ranking will be stored.

Utility
------------

.. rst:directive:: DataCharacteristicsPlotting.R

    .. raw:: html

      <details>
      <summary style="color:green;"><font size="-1">[sources]</font></summary>

    .. literalinclude:: ../../code/R/DataCharacteristicsPlotting.R
      :language: R

    .. raw:: html

      </details>

    Creates plots to show some characteristics of a given expression data set and its class labels.
    Currently supported plots that can be selected: density plots (density), box plot (box), and mds plot (mds).
    Invoked by :class:`evaluation.DatasetEvaluator`.

    :param args: the input parameters parsed from the command line, consisting of a) the absolute path to the input expression file, b) the absolute path to the output directory where the plots will be stored, c) the separator to use for reading the input expression file, d) a boolean value whether the input expression data is labeled or not, and e) a list of option names that define what plots are created. Currently supported: density (density plot), box (boxplot of expression values), mds).

.. rst:directive:: UpsetDiagramCreation.R

  .. raw:: html

    <details>
    <summary style="color:green;"><font size="-1">[sources]</font></summary>

  .. literalinclude:: ../../code/R/UpsetDiagramCreation.R
    :language: R

  .. raw:: html

    </details>

    Uses the UpSetR package to create an upset diagram for a given set of features.
    Invoked by :class:`evaluation.RankingsEvaluator` and :class:`evaluation.AnnotationEvaluator`.

    :param args: the input parameters parsed from the command line, consisting of a) the absolute path to the output file where to store the created plot, b) the number of top k features for which to compute the feature set overlaps, c) absolute path to the input directory containing the input files, d) a string of color ids separated by "_", used for giving every feature ranking a unique color, and e) a list of input files containing the rankings, where the rankings order corresponds to the order of colors.

.. rst:directive:: IdentifierMapping.R

    .. raw:: html

      <details>
      <summary style="color:green;"><font size="-1">[sources]</font></summary>

    .. literalinclude:: ../../code/R/IdentifierMapping.R
      :language: R

    .. raw:: html

      </details>

    The current implementation sends the identifiers for mapping in chunks of 10.000 identifiers (that was one desperate try to improve biomaRt stability, but it probably did not help...).
    Invoked by :class:`knowledgebases.BioMART`.

    :param args: the input parameters parsed from the command line, consisting of a) the original ID format (corresponding to biomaRt identifiers), e.g. ensembl_gene_id, b) the desired ID format (corresponding to biomaRt identifiers), e.g. hgnc_symbol, c) the absolute path to the input file, which contains one identifier per line, and d) the absolute path to the output file where the mapping will be stored.
