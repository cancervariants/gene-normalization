CREATE MATERIALIZED VIEW record_lookup_view AS
SELECT gc.concept_id,
       gc.symbol_status,
       gc.label,
       gc.strand,
       gc.location_annotations,
       gc.locations,
       gc.gene_type,
       ga.aliases,
       gas.associated_with,
       gps.previous_symbols,
       gs.symbol,
       gx.xrefs,
       gc.source,
       gc.merge_ref,
       lower(gc.concept_id) AS concept_id_lowercase
FROM gene_concepts gc
FULL JOIN (
    SELECT ga_1.concept_id, array_agg(ga_1.alias) AS aliases
    FROM gene_aliases ga_1
    GROUP BY ga_1.concept_id
) ga ON gc.concept_id::text = ga.concept_id::text
FULL JOIN (
    SELECT gas_1.concept_id, array_agg(gas_1.associated_with) AS associated_with
    FROM gene_associations gas_1
    GROUP BY gas_1.concept_id
) gas ON gc.concept_id::text = gas.concept_id::text
FULL JOIN (
    SELECT gps_1.concept_id, array_agg(gps_1.prev_symbol) AS previous_symbols
    FROM gene_previous_symbols gps_1
    GROUP BY gps_1.concept_id
) gps ON gc.concept_id::text = gps.concept_id::text
FULL JOIN gene_symbols gs ON gc.concept_id::text = gs.concept_id::text
FULL JOIN (
    SELECT gx_1.concept_id, array_agg(gx_1.xref) AS xrefs
    FROM gene_xrefs gx_1
    GROUP BY gx_1.concept_id
) gx ON gc.concept_id::text = gx.concept_id::text;
