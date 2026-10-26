<!-- Generated from src/peskas_api/schema/field_metadata.py by
     `python -m peskas_api.schema.fields_doc`. Do not edit by hand. -->

# Fields

Every column each endpoint returns, in order. The API serves the same
descriptions at `/metadata/{dataset}`, which needs no key.

## `/data/landings`

Fish landing records with catch and trip information. 23 columns.

| Column | Type | Unit | Description |
| --- | --- | --- | --- |
| `survey_organization` | string |  | Organization that collected the record: KEFS (Kenya Fisheries Service) and WCS (Wildlife Conservation Society) in Kenya, ZAFIRI (Zanzibar Fisheries and Marine Resources Research Institute) in Zanzibar, MAF (Ministry of Agriculture and Fisheries) in Timor-Leste, and DINAPA (National Directorate of Fisheries and Aquaculture, formerly ADNAP) in Mozambique. A country can run more than one survey programme at once, on different instruments: Kenya publishes WCS and KEFS side by side, and they differ in what they collect (WCS records no trip duration and no length) and in how catch is sampled (KEFS weighs the whole catch and identifies a sample of it, so its catch rows are not meant to sum to tot_catch_kg). survey_id identifies the form version, not the organization, so it cannot be used for this. Values: `KEFS`, `WCS`, `ZAFIRI`, `MAF`, `DINAPA`. |
| `survey_id` | string |  | Unique identifier for the survey from which this record was collected. |
| `trip_id` | string |  | Unique identifier for the fishing trip. |
| `landing_date` | date | ISO 8601 date format (YYYY-MM-DD) | Date when the catch was landed (brought to shore). |
| `gaul_1_code` | string |  | GAUL (Global Administrative Unit Layers) level 1 administrative code. The administrative boundaries at the level 1 dataset distinguishes States, Provinces, Departments and equivalent. [Reference](https://data.apps.fao.org/catalog/dataset/34f97afc-6218-459a-971d-5af1162d318a/resource/d472b55c-a1e0-4c9c-9ccb-8bf10c8bf0a3) |
| `gaul_1_name` | string |  | Human-readable name of the GAUL level 1 administrative unit. [Reference](https://data.apps.fao.org/catalog/dataset/34f97afc-6218-459a-971d-5af1162d318a/resource/d472b55c-a1e0-4c9c-9ccb-8bf10c8bf0a3) |
| `gaul_2_code` | string |  | GAUL (Global Administrative Unit Layers) level 2 administrative code. The administrative boundaries at the level 2 dataset distinguishes Districts and equivalent. [Reference](https://data.apps.fao.org/catalog/dataset/60b23906-f21a-49ef-8424-f3645e70264e/resource/a4d23085-c6be-4924-b4be-1df45cec4168) |
| `gaul_2_name` | string |  | Human-readable name of the GAUL level 2 administrative unit. [Reference](https://data.apps.fao.org/catalog/dataset/60b23906-f21a-49ef-8424-f3645e70264e/resource/a4d23085-c6be-4924-b4be-1df45cec4168) |
| `landing_site` | string |  | Location at which boats land their catch. A landing site may be the same as the homeport or base port but it can also be different. Recording of fishing activities tend to be conducted in the vessel homeport or base port, while sampling and recording of catches and species composition, landing prices, etc. are usually undertaken at landing sites. [Ontology](http://w3id.org/aqfo/aqfo_00000030) |
| `n_fishers` | integer |  | The total number of people actively fishing on a fishing trip. [Ontology](http://w3id.org/aqfo/aqfo_00000022) |
| `trip_duration_hrs` | float | hours | Refers to the duration of fishing, measured in time (normally days or hours) between departure and return time and date. [Ontology](http://w3id.org/aqfo/aqfo_00002011) |
| `gear` | string |  | A fishing gear is a tool or method used to catch fish, such as hook-and-line, trawl net, gillnet, pot, trap, spear, manual collection etc. Values: `hand_line`, `net`, `trap`, `spear`, `longline`, `trawl`. [Ontology](http://w3id.org/aqfo/aqfo_00002220) |
| `vessel_type` | string |  | Refers to any water vehicle that operates above or under the water surface with or without an engine or other form of propulsion. Values: `outrigger`, `dhow`, `canoe`. [Ontology](http://w3id.org/aqfo/aqfo_00001013) |
| `catch_habitat` | string |  | The place where an organism lives or the place one would go to find it. The habitat is the organisms address, and the ecological niche its profession, biologically speaking. Values: `reef`, `pelagic`, `demersal`, `coastal`, `offshore`. [Ontology](http://w3id.org/aqfo/aqfo_00000023) |
| `catch_outcome` | integer |  | Binary indicator of whether the fishing trip resulted in any catch. Use 1 for a positive outcome (at least one catch recorded), 0 for no catch. Values: `0`, `1`. |
| `n_catch` | integer |  | Number of distinct catch records reported for the trip. A catch record is defined by a unique combination of taxon (e.g., FAO ASFIS code) and size/length class. For example, two tunas in different length classes (e.g., 10–15 cm and 20–25 cm) count as two catches. |
| `catch_taxon` | string |  | 3-alpha code identifying the species or taxonomic group according to the FAO ASFIS List of Species for Fishery Statistics Purposes. Values: `MZZ`, `SKJ`, `IAX`, `TUN`, `YFT`, `BET`. [Reference](https://www.fao.org/fishery/en/collection/asfis) |
| `scientific_name` | string |  | Full binomial scientific name of the species or taxonomic group, complementing the FAO ASFIS 3-alpha code in catch_taxon (e.g., 'Katsuwonus pelamis' for SKJ). [Reference](https://www.marinespecies.org) |
| `length_cm` | float | cm | Length class associated with the catch record. Although stored as a numeric value, for fish up to 100 cm this field represents membership in predefined length ranges used in data collection: <10, 10–15, 15–20, 20–25, 25–30, 30–40, 40–50, 50–60, 60–70, 70–80, 80–90, 90–100 cm. For fish larger than 1 meter, the enumerator records the measured length in cm (e.g., 110, 130, 145, 200) rather than a range label. [Ontology](http://w3id.org/aqfo/aqfo_00002073) |
| `catch_kg` | float | kg | Weight of the catch in kilograms. |
| `catch_price` | float | local_currency | Price of the catch in local currency. Currency unit depends on the country. [Ontology](http://w3id.org/aqfo/aqfo_00002015) |
| `tot_catch_kg` | float | kg | Total weight of all catches for the entire fishing trip in kilograms. This is the sum of all catch_kg values for the trip. |
| `tot_catch_price` | float | local_currency | Total price of all catches for the entire fishing trip in local currency. This is the sum of all catch_price values for the trip. Currency unit depends on the country. |

- `scope=trip_info` returns `survey_organization`, `survey_id`, `trip_id`, `landing_date`, `gaul_1_code`, `gaul_1_name`, `gaul_2_code`, `gaul_2_name`, `landing_site`, `n_fishers`, `trip_duration_hrs`, `gear`, `vessel_type`, `catch_habitat`, `catch_outcome`, `tot_catch_kg`, `tot_catch_price`.
- `scope=catch_info` returns `survey_id`, `trip_id`, `catch_taxon`, `scientific_name`, `n_catch`, `length_cm`, `catch_kg`, `catch_price`.

## `/data/district-months`

Monthly figures per district: recorded averages and whole-fleet estimates. 23 columns.

| Column | Type | Unit | Description |
| --- | --- | --- | --- |
| `country` | string |  | Country the row belongs to. Values: `kenya`, `mozambique`, `timor`, `zanzibar`. |
| `month` | date | ISO 8601 date format (YYYY-MM-DD) | Month the landings happened in, as its first day. |
| `gaul_1_code` | string |  | GAUL (Global Administrative Unit Layers) level 1 administrative code. The administrative boundaries at the level 1 dataset distinguishes States, Provinces, Departments and equivalent. [Reference](https://data.apps.fao.org/catalog/dataset/34f97afc-6218-459a-971d-5af1162d318a/resource/d472b55c-a1e0-4c9c-9ccb-8bf10c8bf0a3) |
| `gaul_1_name` | string |  | Human-readable name of the GAUL level 1 administrative unit. [Reference](https://data.apps.fao.org/catalog/dataset/34f97afc-6218-459a-971d-5af1162d318a/resource/d472b55c-a1e0-4c9c-9ccb-8bf10c8bf0a3) |
| `gaul_2_code` | string |  | GAUL (Global Administrative Unit Layers) level 2 administrative code. The administrative boundaries at the level 2 dataset distinguishes Districts and equivalent. [Reference](https://data.apps.fao.org/catalog/dataset/60b23906-f21a-49ef-8424-f3645e70264e/resource/a4d23085-c6be-4924-b4be-1df45cec4168) |
| `gaul_2_name` | string |  | Human-readable name of the GAUL level 2 administrative unit. [Reference](https://data.apps.fao.org/catalog/dataset/60b23906-f21a-49ef-8424-f3645e70264e/resource/a4d23085-c6be-4924-b4be-1df45cec4168) |
| `n_submissions` | integer | landings | Landings (fishing trips) recorded by enumerators in the district that month and kept after validation. 0 when none were recorded: the row then shows a gap in data collection, and its other figures are empty. Landings whose site is not matched to a district are not counted in any row. |
| `mean_n_fishers` | float | fishers | Average number of fishers on a recorded trip. |
| `mean_trip_duration_hrs` | float | hours | Average duration of a recorded trip. Empty where the survey does not record it. |
| `mean_catch_kg` | float | kg | Average total catch of a recorded trip. |
| `mean_catch_price` | float | local_currency | Average value of a recorded trip's catch, in local currency. |
| `mean_price_kg` | float | local_currency per kg | Average price per kilogram: each recorded trip's catch value divided by its catch weight, averaged over the trips. |
| `mean_cpue` | float | kg per fisher per hour | Average catch per unit of effort: each recorded trip's catch divided by its fishers and its hours of fishing, averaged over the trips. |
| `mean_rpue` | float | local_currency per fisher per hour | Average revenue per unit of effort: each recorded trip's catch value divided by its fishers and its hours of fishing, averaged over the trips. |
| `estimated_fishing_trips` | float | trips | Fishing trips made by all the district's boats that month, by the GPS tracker method: trips per GPS-tracked boat, scaled up to the boats counted in the census. In Timor-Leste, whose rows are municipalities, it comes from the Timor pipeline's own model instead, and is given for every month from 2018. |
| `estimated_catch_tn` | float | tonnes | Catch landed by all the district's boats that month, by the GPS tracker method: catch per trip times the estimated trips. Empty when fewer than 10 landings were recorded. In Timor-Leste, whose rows are municipalities, it comes from the Timor pipeline's own model instead, and is given for every month from 2018. |
| `estimated_revenue` | float | local_currency | Value of that catch, in local currency. Empty when fewer than 10 landings were recorded. In Timor-Leste, whose rows are municipalities, it comes from the Timor pipeline's own model instead, and is given for every month from 2018. |
| `sampling_rate` | float | share | Share of the district's census boats that carried a GPS tracker that month. It says how far to trust the GPS tracker estimates: 0.3 or more is good, 0.1 to 0.3 fair, below 0.1 weak. Empty in Timor-Leste, whose estimates do not use the trackers. |
| `estimated_fishing_trips_fao` | float | trips | Fishing trips made by all the district's boats that month, by the FAO ARTFISH method: boats counted in the census times the days they fished, as fishers report them. |
| `estimated_catch_tn_fao` | float | tonnes | Catch landed by all the district's boats that month, by the FAO ARTFISH method: catch per trip times those trips, for each boat and gear group (boat type alone in Mozambique). Empty when fewer than 10 landings were recorded. |
| `estimated_revenue_fao` | float | local_currency | Value of that catch, in local currency. Empty when fewer than 10 landings were recorded. |
| `relative_error_catch_fao` | float | share | How far the true catch may differ from estimated_catch_tn_fao, at 90% confidence, as a share of it: 0.44 means within 44%. FAO's OPEN ARTFISH Toolkit aims for 0.15 or less and accepts up to 0.20. The Toolkit gives this error for each boat and gear group; the district's adds up theirs, which makes it a cautious figure. Empty where no group's error can be measured. |
| `relative_error_revenue_fao` | float | share | How far the true revenue may differ from estimated_revenue_fao, at 90% confidence, as a share of it: 0.44 means within 44%. FAO's OPEN ARTFISH Toolkit aims for 0.15 or less and accepts up to 0.20. The Toolkit gives this error for each boat and gear group; the district's adds up theirs, which makes it a cautious figure. Empty where no group's error can be measured. |
