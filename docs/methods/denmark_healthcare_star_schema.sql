-- Denmark health-care footprint star schema
-- PostgreSQL-style template. Types can be adapted to DuckDB/Fabric/Snowflake.

CREATE TABLE dim_time (
    time_key            INTEGER PRIMARY KEY,
    year                INTEGER NOT NULL,
    price_year          INTEGER,
    period_type         VARCHAR(30) DEFAULT 'calendar_year'
);

CREATE TABLE dim_geography (
    geography_key       BIGINT PRIMARY KEY,
    iso_code            VARCHAR(10),
    geography_name      VARCHAR(200) NOT NULL,
    geography_level     VARCHAR(30), -- country, region, municipality, MRIO_region
    eu_flag              BOOLEAN,
    denmark_flag         BOOLEAN
);

CREATE TABLE dim_industry (
    industry_key        BIGINT PRIMARY KEY,
    classification      VARCHAR(30), -- DB07/NACE/ISIC/EXIOBASE/EORA
    industry_code       VARCHAR(40),
    industry_name       VARCHAR(300),
    parent_code         VARCHAR(40),
    hierarchy_level     INTEGER
);

CREATE TABLE dim_product (
    product_key         BIGINT PRIMARY KEY,
    classification      VARCHAR(30), -- SUT/CPA/COICOP
    product_code        VARCHAR(40),
    product_name        VARCHAR(300),
    parent_code         VARCHAR(40)
);

CREATE TABLE dim_health_function (
    health_function_key BIGINT PRIMARY KEY,
    sha_hc_code         VARCHAR(30),
    function_name       VARCHAR(300)
);

CREATE TABLE dim_provider (
    provider_key        BIGINT PRIMARY KEY,
    sha_hp_code         VARCHAR(30),
    provider_name       VARCHAR(300)
);

CREATE TABLE dim_financing (
    financing_key       BIGINT PRIMARY KEY,
    sha_hf_code         VARCHAR(30),
    financing_name      VARCHAR(300)
);

CREATE TABLE dim_impact (
    impact_key          BIGINT PRIMARY KEY,
    impact_code         VARCHAR(50),
    impact_name         VARCHAR(200),
    level_type          VARCHAR(20), -- inventory/midpoint/endpoint
    default_unit        VARCHAR(50),
    method_name         VARCHAR(100),
    method_version      VARCHAR(50)
);

CREATE TABLE dim_flow (
    flow_key            BIGINT PRIMARY KEY,
    flow_name           VARCHAR(200),
    flow_type           VARCHAR(50), -- GHG, air pollutant, water, material, waste
    cas_number          VARCHAR(30),
    base_unit           VARCHAR(50),
    gwp_value           NUMERIC,
    gwp_version         VARCHAR(50)
);

CREATE TABLE dim_supply_layer (
    layer_key           INTEGER PRIMARY KEY,
    layer_number        INTEGER,
    layer_name          VARCHAR(100)
);

CREATE TABLE dim_price_basis (
    price_key           INTEGER PRIMARY KEY,
    currency            VARCHAR(10),
    price_type          VARCHAR(30), -- basic/purchaser
    valuation           VARCHAR(30), -- current/constant/chained
    base_year           INTEGER
);

CREATE TABLE dim_scenario (
    scenario_key        BIGINT PRIMARY KEY,
    scenario_name       VARCHAR(200),
    model_version       VARCHAR(100),
    mrio_database       VARCHAR(100),
    mrio_version        VARCHAR(50)
);

CREATE TABLE dim_source (
    source_key          BIGINT PRIMARY KEY,
    institution         VARCHAR(200),
    dataset_name        VARCHAR(300),
    table_id            VARCHAR(100),
    dataset_version     VARCHAR(100),
    extraction_date     DATE,
    source_url          TEXT
);

CREATE TABLE dim_scope (
    scope_key           BIGINT PRIMARY KEY,
    accounting_boundary VARCHAR(50), -- territorial/consumption
    capital_included    BOOLEAN,
    imports_included    BOOLEAN,
    patient_travel      BOOLEAN,
    staff_travel        BOOLEAN,
    bottomup_included   BOOLEAN,
    notes               TEXT
);

CREATE TABLE fact_health_expenditure (
    expenditure_id      BIGINT PRIMARY KEY,
    time_key            INTEGER REFERENCES dim_time(time_key),
    health_function_key BIGINT REFERENCES dim_health_function(health_function_key),
    provider_key        BIGINT REFERENCES dim_provider(provider_key),
    financing_key       BIGINT REFERENCES dim_financing(financing_key),
    product_key         BIGINT REFERENCES dim_product(product_key),
    industry_key        BIGINT REFERENCES dim_industry(industry_key),
    price_key           INTEGER REFERENCES dim_price_basis(price_key),
    source_key          BIGINT REFERENCES dim_source(source_key),
    amount_dkk          NUMERIC NOT NULL,
    mapping_weight      NUMERIC,
    health_boundary_flag BOOLEAN,
    quality_flag        VARCHAR(40)
);

CREATE TABLE fact_io_flow (
    io_flow_id          BIGINT PRIMARY KEY,
    time_key            INTEGER REFERENCES dim_time(time_key),
    supplier_industry_key BIGINT REFERENCES dim_industry(industry_key),
    supplier_product_key BIGINT REFERENCES dim_product(product_key),
    user_industry_key   BIGINT REFERENCES dim_industry(industry_key),
    geography_key       BIGINT REFERENCES dim_geography(geography_key),
    price_key           INTEGER REFERENCES dim_price_basis(price_key),
    source_key          BIGINT REFERENCES dim_source(source_key),
    value_dkk           NUMERIC,
    domestic_import_flag VARCHAR(20),
    valuation_component VARCHAR(50)
);

CREATE TABLE fact_environmental_extension (
    extension_id        BIGINT PRIMARY KEY,
    time_key            INTEGER REFERENCES dim_time(time_key),
    geography_key       BIGINT REFERENCES dim_geography(geography_key),
    industry_key        BIGINT REFERENCES dim_industry(industry_key),
    flow_key            BIGINT REFERENCES dim_flow(flow_key),
    impact_key          BIGINT REFERENCES dim_impact(impact_key),
    source_key          BIGINT REFERENCES dim_source(source_key),
    physical_quantity   NUMERIC,
    output_dkk          NUMERIC,
    direct_intensity_per_dkk NUMERIC,
    uncertainty_sd      NUMERIC
);

CREATE TABLE fact_footprint_total (
    footprint_id        BIGINT PRIMARY KEY,
    time_key            INTEGER REFERENCES dim_time(time_key),
    impact_key          BIGINT REFERENCES dim_impact(impact_key),
    scenario_key        BIGINT REFERENCES dim_scenario(scenario_key),
    scope_key           BIGINT REFERENCES dim_scope(scope_key),
    value               NUMERIC,
    unit                VARCHAR(50),
    sd                  NUMERIC,
    p025                NUMERIC,
    p975                NUMERIC,
    national_total_same_boundary NUMERIC,
    national_share_pct  NUMERIC,
    population          NUMERIC,
    per_capita_value    NUMERIC,
    health_expenditure_dkk NUMERIC,
    intensity_per_dkk   NUMERIC
);

CREATE TABLE fact_health_category_footprint (
    time_key            INTEGER REFERENCES dim_time(time_key),
    impact_key          BIGINT REFERENCES dim_impact(impact_key),
    health_function_key BIGINT REFERENCES dim_health_function(health_function_key),
    provider_key        BIGINT REFERENCES dim_provider(provider_key),
    product_key         BIGINT REFERENCES dim_product(product_key),
    scenario_key        BIGINT REFERENCES dim_scenario(scenario_key),
    footprint_value     NUMERIC,
    share_pct           NUMERIC,
    expenditure_dkk     NUMERIC,
    footprint_per_dkk   NUMERIC
);

CREATE TABLE fact_supplier_footprint (
    time_key            INTEGER REFERENCES dim_time(time_key),
    impact_key          BIGINT REFERENCES dim_impact(impact_key),
    industry_key        BIGINT REFERENCES dim_industry(industry_key),
    geography_key       BIGINT REFERENCES dim_geography(geography_key),
    scenario_key        BIGINT REFERENCES dim_scenario(scenario_key),
    footprint_value     NUMERIC,
    share_pct           NUMERIC,
    direct_indirect     VARCHAR(20)
);

CREATE TABLE fact_production_layer (
    time_key            INTEGER REFERENCES dim_time(time_key),
    impact_key          BIGINT REFERENCES dim_impact(impact_key),
    layer_key           INTEGER REFERENCES dim_supply_layer(layer_key),
    geography_key       BIGINT REFERENCES dim_geography(geography_key),
    scenario_key        BIGINT REFERENCES dim_scenario(scenario_key),
    footprint_value     NUMERIC,
    cumulative_value    NUMERIC,
    cumulative_share_pct NUMERIC,
    truncation_error_pct NUMERIC
);

CREATE TABLE fact_geographic_footprint (
    time_key            INTEGER REFERENCES dim_time(time_key),
    impact_key          BIGINT REFERENCES dim_impact(impact_key),
    consuming_geography_key BIGINT REFERENCES dim_geography(geography_key),
    producing_geography_key BIGINT REFERENCES dim_geography(geography_key),
    scenario_key        BIGINT REFERENCES dim_scenario(scenario_key),
    footprint_value     NUMERIC,
    share_pct           NUMERIC
);

CREATE TABLE fact_ghg_species (
    time_key            INTEGER REFERENCES dim_time(time_key),
    flow_key            BIGINT REFERENCES dim_flow(flow_key),
    scope_key           BIGINT REFERENCES dim_scope(scope_key),
    scenario_key        BIGINT REFERENCES dim_scenario(scenario_key),
    mass                NUMERIC,
    mass_unit           VARCHAR(30),
    gwp_value           NUMERIC,
    gwp_version         VARCHAR(50),
    co2e_value          NUMERIC,
    share_of_total_ghg_pct NUMERIC
);

CREATE TABLE fact_footprint_trend (
    time_key            INTEGER REFERENCES dim_time(time_key),
    impact_key          BIGINT REFERENCES dim_impact(impact_key),
    scenario_key        BIGINT REFERENCES dim_scenario(scenario_key),
    total_footprint     NUMERIC,
    per_capita_footprint NUMERIC,
    health_expenditure_dkk NUMERIC,
    footprint_intensity_per_dkk NUMERIC,
    population          NUMERIC,
    index_base100       NUMERIC,
    yoy_change_pct      NUMERIC
);

CREATE TABLE fact_uncertainty_run (
    run_id              BIGINT PRIMARY KEY,
    time_key            INTEGER REFERENCES dim_time(time_key),
    impact_key          BIGINT REFERENCES dim_impact(impact_key),
    scenario_key        BIGINT REFERENCES dim_scenario(scenario_key),
    footprint_value     NUMERIC,
    random_seed         BIGINT,
    perturbation_model  VARCHAR(80),
    q_uncertainty_version VARCHAR(80),
    t_uncertainty_version VARCHAR(80),
    y_uncertainty_version VARCHAR(80)
);

CREATE TABLE fact_health_damage (
    damage_id           BIGINT PRIMARY KEY,
    time_key            INTEGER REFERENCES dim_time(time_key),
    impact_key          BIGINT REFERENCES dim_impact(impact_key),
    flow_key            BIGINT REFERENCES dim_flow(flow_key),
    scenario_key        BIGINT REFERENCES dim_scenario(scenario_key),
    inventory_value     NUMERIC,
    midpoint_value      NUMERIC,
    characterization_method VARCHAR(100),
    endpoint_method     VARCHAR(100),
    daly_value          NUMERIC,
    daly_per_billion_dkk NUMERIC,
    uncertainty_lower   NUMERIC,
    uncertainty_upper   NUMERIC,
    endpoint_validity_flag VARCHAR(40)
);

CREATE TABLE fact_bottomup_source (
    bottomup_id         BIGINT PRIMARY KEY,
    time_key            INTEGER REFERENCES dim_time(time_key),
    provider_key        BIGINT REFERENCES dim_provider(provider_key),
    impact_key          BIGINT REFERENCES dim_impact(impact_key),
    source_key          BIGINT REFERENCES dim_source(source_key),
    activity_type       VARCHAR(100),
    activity_quantity   NUMERIC,
    activity_unit       VARCHAR(50),
    emission_factor     NUMERIC,
    factor_unit         VARCHAR(80),
    footprint_value     NUMERIC,
    overlap_io_sector_key BIGINT REFERENCES dim_industry(industry_key),
    io_amount_removed_or_adjusted NUMERIC,
    double_counting_rule TEXT,
    uncertainty_sd      NUMERIC
);


-- Many-to-many bridge tables are intentionally separate from dimensions/facts.
-- They preserve transparent concordance weights and prevent hidden allocation logic.

CREATE TABLE bridge_health_to_economic_node (
    bridge_id            BIGINT PRIMARY KEY,
    time_key             INTEGER REFERENCES dim_time(time_key),
    health_function_key  BIGINT REFERENCES dim_health_function(health_function_key),
    provider_key         BIGINT REFERENCES dim_provider(provider_key),
    financing_key        BIGINT REFERENCES dim_financing(financing_key),
    product_key          BIGINT REFERENCES dim_product(product_key),
    industry_key         BIGINT REFERENCES dim_industry(industry_key),
    source_key           BIGINT REFERENCES dim_source(source_key),
    allocation_weight    NUMERIC NOT NULL,
    weighting_basis      VARCHAR(80), -- expenditure/output/activity/expert
    mapping_method       VARCHAR(100),
    confidence_grade     VARCHAR(20),
    notes                TEXT
);

CREATE TABLE bridge_dk_to_mrio (
    bridge_id            BIGINT PRIMARY KEY,
    time_key             INTEGER REFERENCES dim_time(time_key),
    dk_product_key       BIGINT REFERENCES dim_product(product_key),
    dk_industry_key      BIGINT REFERENCES dim_industry(industry_key),
    mrio_industry_key    BIGINT REFERENCES dim_industry(industry_key),
    source_key           BIGINT REFERENCES dim_source(source_key),
    allocation_weight    NUMERIC NOT NULL,
    domestic_import_flag VARCHAR(20),
    mapping_method       VARCHAR(100),
    confidence_grade     VARCHAR(20)
);

CREATE TABLE bridge_impact_characterization (
    bridge_id            BIGINT PRIMARY KEY,
    flow_key             BIGINT REFERENCES dim_flow(flow_key),
    impact_key           BIGINT REFERENCES dim_impact(impact_key),
    characterization_factor NUMERIC,
    factor_unit          VARCHAR(100),
    source_key           BIGINT REFERENCES dim_source(source_key),
    valid_from_year      INTEGER,
    valid_to_year        INTEGER,
    uncertainty_sd       NUMERIC
);
