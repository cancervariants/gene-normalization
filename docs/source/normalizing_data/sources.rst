Sources
=======

HGNC
----

`The HUGO Gene Nomenclature Committee database <https://www.genenames.org/>`_ provides records (referred to as *Symbol Reports*) for protein-coding genes, pseudogenes, and non-coding RNA genes as designated by the HGNC. :footcite:p:`Hgnc2023` Symbol reports contain approved symbols, previously-used symbols, full names, and other relevant information for each approved gene. The Gene Normalizer extracts nomenclature, aliases, cross-references, locus types, and VRS Chromosome Locations for all HGNC gene records. Data is extracted from the latest HGNC JSON release (``hgnc_complete_set.json``) provided on the `HGNC archive page <https://www.genenames.org/download/archive/>`_.

Ensembl
-------

`Ensembl <https://ensembl.org>`_ is an online genome browser provided by EMBL-EBI to support research in vertebrates and model organisms. :footcite:p:`Ensembl2023` The Gene Normalizer extracts human gene identifiers, names, symbols, cross-references, Ensembl biotypes, and genomic locations for each Ensembl gene record. Data is pulled from the latest Ensembl release listed on the `EBI FTP server <https://ftp.ensembl.org/pub/current_gff3/homo_sapiens/Homo_sapiens.GRCh38.109.gff3.gz>`_.

NCBI Gene
------------------

The `NCBI Gene Database <https://www.ncbi.nlm.nih.gov/gene/>`_ is a service provided under the NCBI Database mantle, relaying gene nomenclature, reference sequences, pathways, and cross-references to other genomic resources. :footcite:p:`Ncbi2022` The Gene Normalizer selects all records for *homo sapiens* and gathers names, aliases, cross-references, gene types, and VRS Sequence and Chromosome Locations. Data is sourced from the latest Homo Sapiens release provided on the `NCBI FTP server <https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/>`_.

References
__________

.. footbibliography::
