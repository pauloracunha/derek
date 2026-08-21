# Esquema das tabelas carregadas

Gerado automaticamente por `pipeline/s02_load.py` em 2026-08-13T16:22:37.199839+00:00. Não editar à mão — reflete sempre a execução mais recente de `s02_load.py`.

## `ancient` (1342 linhas)

| Campo | Tipo |
|---|---|
| `extra` | `VARCHAR` |
| `friendly_id` | `VARCHAR` |
| `geojson_file` | `VARCHAR` |
| `geometry_credit` | `VARCHAR` |
| `id` | `VARCHAR` |
| `identifications` | `STRUCT("class" VARCHAR, description VARCHAR, id VARCHAR, id_source VARCHAR, media STRUCT(thumbnail STRUCT(credit VARCHAR, credit_url VARCHAR, description VARCHAR, file VARCHAR, image_id VARCHAR, placeholder VARCHAR, "role" VARCHAR)), resolutions STRUCT(ancient_geometry VARCHAR, best_path_score HUGEINT, "class" VARCHAR, description VARCHAR, geojson_roles STRUCT(precise STRUCT(description VARCHAR, geometry_credit VARCHAR, id VARCHAR), representative_point STRUCT(description VARCHAR, id VARCHAR), simplified_precise STRUCT(description VARCHAR, geometry_credit VARCHAR, id VARCHAR), geometry STRUCT(description VARCHAR, id VARCHAR), point STRUCT(description VARCHAR, id VARCHAR), "local" STRUCT(description VARCHAR, geometry_credit VARCHAR, id VARCHAR), center STRUCT(description VARCHAR, id VARCHAR), simplified_geometry STRUCT(description VARCHAR, id VARCHAR), settlement STRUCT(description VARCHAR, id VARCHAR), simplified_local STRUCT(description VARCHAR, geometry_credit VARCHAR, id VARCHAR)), land_or_water VARCHAR, lonlat VARCHAR, lonlat_type VARCHAR, modern_basis_id VARCHAR, paths STRUCT(ancient_id VARCHAR, identification_i BIGINT, modern_id VARCHAR, modifier VARCHAR, special VARCHAR)[][], precise_geometry_id VARCHAR, "type" VARCHAR, geometry_id VARCHAR, local_geometry_id VARCHAR, best_time_score HUGEINT, media STRUCT(thumbnail STRUCT(credit VARCHAR, description VARCHAR, file VARCHAR, image_id VARCHAR, placeholder VARCHAR, "role" VARCHAR, credit_url VARCHAR)), geometry_radius_meters BIGINT, modifier VARCHAR, "in" VARCHAR, special VARCHAR)[], score STRUCT(time_best_fits HUGEINT[], time_intercept HUGEINT, time_r_squared DOUBLE, time_slope DOUBLE, time_total HUGEINT, time_values HUGEINT[], vote_average HUGEINT, vote_count BIGINT, vote_total HUGEINT), "types" VARCHAR[], votes STRUCT(tags STRUCT(confidence_likely BIGINT, confidence_possible BIGINT, confidence_yes BIGINT, identified_been BIGINT, identified_is BIGINT, authority_usually BIGINT, confidence_map BIGINT, confidence_mostlikely BIGINT, identified_adjective BIGINT, confidence_unlikely BIGINT, authority_scholar BIGINT, confidence_no BIGINT, "unknown" BIGINT, authority_traditional BIGINT, uncertain BIGINT, authority_variant BIGINT, authority_parallel BIGINT, authority_preserved BIGINT, authority_old BIGINT)), geometry_radius_meters BIGINT, modifier VARCHAR, geometry_id VARCHAR, "comment" VARCHAR, special VARCHAR, contains BIGINT[], contained_in BIGINT[])[]` |
| `kml_file` | `VARCHAR` |
| `linked_data` | `STRUCT(s294e03 STRUCT(id VARCHAR, ids VARCHAR[]), s3b25cf STRUCT(id VARCHAR, ids VARCHAR[]), s7cc8b2 STRUCT(id VARCHAR, modifier VARCHAR), s7f5356 STRUCT("name" VARCHAR, review VARCHAR, url VARCHAR), s85af0b STRUCT(biblemapper_locids_parameters BIGINT[], biblemapper_bmid_parameters VARCHAR[]), sd4d471 STRUCT(id VARCHAR, ids VARCHAR[], review VARCHAR), sf42caf STRUCT(modifier VARCHAR, "name" VARCHAR, url VARCHAR), sb3fe88 STRUCT(id VARCHAR, ids VARCHAR[]), s2428ed STRUCT(data_url VARCHAR, id VARCHAR, url VARCHAR), s454643 STRUCT(data_url VARCHAR, id VARCHAR, url VARCHAR))` |
| `media` | `STRUCT(thumbnail STRUCT(credit VARCHAR, credit_url VARCHAR, description VARCHAR, file VARCHAR, image_id VARCHAR, placeholder VARCHAR, "role" VARCHAR))` |
| `modern_associations` | `MAP(VARCHAR, STRUCT(identification_ids BIGINT[][], "name" VARCHAR, score HUGEINT, url_slug VARCHAR))` |
| `preceding_article` | `VARCHAR` |
| `translation_name_counts` | `MAP(VARCHAR, BIGINT)` |
| `types` | `VARCHAR[]` |
| `url_slug` | `VARCHAR` |
| `verses` | `STRUCT(instance_types STRUCT("name" BIGINT, common_noun BIGINT, "partial" BIGINT, people_group BIGINT, no_translation BIGINT, helper BIGINT, person BIGINT, combined BIGINT), osis VARCHAR, readable VARCHAR, sort VARCHAR, translations VARCHAR[], usx VARCHAR, alternate_roots MAP(VARCHAR, BIGINT), alternate_verses STRUCT(csb VARCHAR, kjv VARCHAR, leb VARCHAR, nasb VARCHAR, net VARCHAR, niv VARCHAR, nkjv VARCHAR, nlt VARCHAR, nrsv VARCHAR))[]` |
| `comment` | `VARCHAR` |
| `identification_sources` | `STRUCT(s3f220c STRUCT(title VARCHAR, titles VARCHAR[]), s611b94 MAP(VARCHAR, JSON), s7eb9df MAP(VARCHAR, VARCHAR), s7f046e STRUCT(page VARCHAR, pages VARCHAR[]), s9703b2 MAP(VARCHAR, VARCHAR), sdf0c9d STRUCT(page VARCHAR, pages VARCHAR[], "map" VARCHAR), s0592d6 STRUCT(title VARCHAR, titles VARCHAR[]), s092bb0 STRUCT(title VARCHAR, page VARCHAR, titles VARCHAR[]), s0dea33 STRUCT(title VARCHAR, titles VARCHAR[]), s284e5a MAP(VARCHAR, JSON), s30e149 STRUCT(title VARCHAR), s45fd0f STRUCT(page VARCHAR), s46f23a STRUCT(title VARCHAR, titles VARCHAR[]), s51cf7f STRUCT(title VARCHAR, titles VARCHAR[], page VARCHAR, "map" VARCHAR), s565ee7 MAP(VARCHAR, JSON), s628590 STRUCT(title VARCHAR), s6cb875 MAP(VARCHAR, JSON), s6ce624 STRUCT(title VARCHAR, titles VARCHAR[]), s73c38d STRUCT(title VARCHAR, titles VARCHAR[]), s876c69 STRUCT(title VARCHAR, titles VARCHAR[]), s8ccb87 STRUCT(title VARCHAR, titles VARCHAR[]), s93d4c1 STRUCT(title VARCHAR), s95bf51 STRUCT(title VARCHAR), s9bf83d MAP(VARCHAR, VARCHAR), sa4a163 STRUCT(title VARCHAR, titles VARCHAR[]), sad8eb0 MAP(VARCHAR, JSON), sc3c58f STRUCT("table" VARCHAR, title VARCHAR, "tables" VARCHAR[]), sd4e1db MAP(VARCHAR, VARCHAR), se72732 STRUCT(title VARCHAR), sea6c3d STRUCT(title VARCHAR), sf6c174 STRUCT("map" VARCHAR), sfd1514 STRUCT(title VARCHAR, page VARCHAR), sfd4d34 MAP(VARCHAR, VARCHAR), s024dad STRUCT(title VARCHAR, page VARCHAR, pages VARCHAR[]), s435156 STRUCT(title VARCHAR), s7a948b STRUCT(page VARCHAR, pages VARCHAR[]), sdb4aa3 STRUCT(title VARCHAR, titles VARCHAR[]), s8326e2 STRUCT(title VARCHAR, titles VARCHAR[]), s339b20 STRUCT(title VARCHAR, page VARCHAR, "map" VARCHAR), s559561 STRUCT(title VARCHAR), s77699d STRUCT(title VARCHAR, titles VARCHAR[], page VARCHAR), s17b4fe STRUCT(title VARCHAR, titles VARCHAR[]), s3e99d5 STRUCT(title VARCHAR), s8119db STRUCT(title VARCHAR), sc0d45b STRUCT(titles VARCHAR[], title VARCHAR), s29dcd8 STRUCT(title VARCHAR), s450a3e MAP(VARCHAR, JSON), s71fbbd MAP(VARCHAR, JSON), s85af0b MAP(VARCHAR, JSON), s9c4f74 MAP(VARCHAR, JSON), sa80e89 STRUCT(title VARCHAR, page VARCHAR), sa96597 MAP(VARCHAR, JSON), sc8b133 MAP(VARCHAR, JSON), sf42caf STRUCT(url VARCHAR, title VARCHAR), s327fdd STRUCT(title VARCHAR, titles VARCHAR[]), s3f2d37 STRUCT(pages VARCHAR[], page VARCHAR), s68f055 STRUCT(page VARCHAR, pages VARCHAR[]), s20e780 STRUCT(title VARCHAR, titles VARCHAR[]), s3b2d77 STRUCT(title VARCHAR), s6d958e STRUCT(title VARCHAR), sc6cebc STRUCT(title VARCHAR), sf5ec50 STRUCT(title VARCHAR), s93c633 STRUCT(page VARCHAR, pages VARCHAR[]), s72f20e MAP(VARCHAR, JSON), s61f084 MAP(VARCHAR, JSON), s99de49 MAP(VARCHAR, JSON), se4b739 MAP(VARCHAR, JSON), sb74ec0 STRUCT(title VARCHAR, "table" VARCHAR), s3a5f5d MAP(VARCHAR, JSON), saa5e60 MAP(VARCHAR, JSON), s6e37ab STRUCT(title VARCHAR), s767f22 MAP(VARCHAR, JSON), s938612 MAP(VARCHAR, JSON), sdd21d1 MAP(VARCHAR, JSON), s0d3761 STRUCT(title VARCHAR, page VARCHAR), s495057 STRUCT(title VARCHAR), s8be486 STRUCT(title VARCHAR), s5a64fd MAP(VARCHAR, JSON), s2a6099 STRUCT(url VARCHAR), s81dfc1 MAP(VARCHAR, JSON), s960baf MAP(VARCHAR, JSON), s454643 MAP(VARCHAR, JSON), sf4241b STRUCT(page VARCHAR, pages VARCHAR[]), s4e6beb STRUCT(page VARCHAR), s2d4006 STRUCT(title VARCHAR), sac23e4 STRUCT(title VARCHAR), se6cf71 STRUCT(title VARCHAR), sfe5cce STRUCT(title VARCHAR), s2c15b3 MAP(VARCHAR, JSON), s333922 MAP(VARCHAR, JSON), s6ab0de MAP(VARCHAR, JSON), s769654 MAP(VARCHAR, JSON), sc73fa3 MAP(VARCHAR, JSON), sd3e083 MAP(VARCHAR, JSON), sfbc865 MAP(VARCHAR, JSON), s87e244 MAP(VARCHAR, JSON), scf286a STRUCT("table" VARCHAR), s0ed9d8 STRUCT(url VARCHAR), s2aba5e MAP(VARCHAR, JSON), s972543 MAP(VARCHAR, JSON), sc798d4 MAP(VARCHAR, JSON), s459155 MAP(VARCHAR, JSON), s119d4d MAP(VARCHAR, JSON), s90fc6e STRUCT(title VARCHAR), se5f078 STRUCT(page VARCHAR), s39bfc9 STRUCT(title VARCHAR), sa6a12b MAP(VARCHAR, JSON), safccad STRUCT(url VARCHAR))` |

## `modern` (1596 linhas)

| Campo | Tipo |
|---|---|
| `ancient_associations` | `MAP(VARCHAR, STRUCT("name" VARCHAR, score HUGEINT, url_slug VARCHAR))` |
| `class` | `VARCHAR` |
| `coordinates_source` | `STRUCT(id VARCHAR, source_id VARCHAR, "type" VARCHAR, data_url VARCHAR, url VARCHAR, url_id VARCHAR, modifier VARCHAR, geometry_credit VARCHAR, osm_version BIGINT, wiki_url VARCHAR, "label" VARCHAR, "map" VARCHAR, georeference_id VARCHAR, georeference_url VARCHAR, page VARCHAR, x VARCHAR, y VARCHAR, article VARCHAR)` |
| `epsg_28191` | `VARCHAR` |
| `friendly_id` | `VARCHAR` |
| `geojson_file` | `VARCHAR` |
| `geojson_roles` | `STRUCT(isobands STRUCT(id VARCHAR), representative_point STRUCT(id VARCHAR, geometry_credit VARCHAR), point STRUCT(id VARCHAR, geometry_credit VARCHAR), precision_radius STRUCT(id VARCHAR), geometry STRUCT(id VARCHAR), "local" STRUCT(geometry_credit VARCHAR, id VARCHAR), simplified_local STRUCT(geometry_credit VARCHAR, id VARCHAR), simplified_geometry STRUCT(id VARCHAR), precise STRUCT(geometry_credit VARCHAR, id VARCHAR), simplified_precise STRUCT(geometry_credit VARCHAR, id VARCHAR))` |
| `geometry` | `VARCHAR` |
| `geometry_id` | `VARCHAR` |
| `id` | `VARCHAR` |
| `kml_file` | `VARCHAR` |
| `land_or_water` | `VARCHAR` |
| `lonlat` | `VARCHAR` |
| `media` | `STRUCT(thumbnail STRUCT(credit VARCHAR, credit_url VARCHAR, description VARCHAR, file VARCHAR, image_id VARCHAR, placeholder VARCHAR, quality VARCHAR, "role" VARCHAR), alternate STRUCT(description VARCHAR, image_id VARCHAR, quality VARCHAR)[], near STRUCT(description VARCHAR, image_id VARCHAR, proximity_meters BIGINT, quality VARCHAR)[], google STRUCT(description VARCHAR, image_id VARCHAR, "role" VARCHAR, quality VARCHAR)[], copyrighted STRUCT(description VARCHAR, image_id VARCHAR)[])` |
| `names` | `STRUCT("name" VARCHAR, "type" VARCHAR, url_slug VARCHAR, description VARCHAR)[]` |
| `preceding_article` | `VARCHAR` |
| `precision` | `STRUCT(description VARCHAR, "type" VARCHAR, meters BIGINT, radius_geometry_id VARCHAR, same_as VARCHAR)` |
| `type` | `VARCHAR` |
| `url_slug` | `VARCHAR` |
| `secondary_sources` | `STRUCT(geometry_credit VARCHAR, osm_version BIGINT, source_id VARCHAR, "type" VARCHAR, url VARCHAR, data_url VARCHAR, id VARCHAR, wiki_url VARCHAR, modifier VARCHAR, article VARCHAR, "from" VARCHAR, local_geometry_id VARCHAR, "group" STRUCT(osm_version BIGINT, "type" VARCHAR, url VARCHAR, "comment" VARCHAR)[], georeference_id VARCHAR, georeference_url VARCHAR, "map" VARCHAR, page VARCHAR, "table" VARCHAR, "comment" VARCHAR, url_id VARCHAR, plate VARCHAR, "label" VARCHAR, "until" VARCHAR)[]` |
| `precision_claims` | `VARCHAR[]` |
| `accuracy_claims` | `VARCHAR[]` |
| `geometry_credit` | `VARCHAR` |
| `local_geometry_id` | `VARCHAR` |
| `precise_geometry_id` | `VARCHAR` |
| `custom_lonlat` | `VARCHAR` |
| `root` | `STRUCT(id VARCHAR, modifier VARCHAR, "source" VARCHAR)` |

## `source` (442 linhas)

| Campo | Tipo |
|---|---|
| `amazon_id` | `VARCHAR` |
| `amazon_url` | `VARCHAR` |
| `contributors` | `VARCHAR[]` |
| `display_name` | `VARCHAR` |
| `friendly_id` | `VARCHAR` |
| `google_books_id` | `VARCHAR` |
| `google_books_url` | `VARCHAR` |
| `id` | `VARCHAR` |
| `type` | `VARCHAR` |
| `worldcat_id` | `VARCHAR` |
| `worldcat_url` | `VARCHAR` |
| `year` | `BIGINT` |
| `url` | `VARCHAR` |
| `logos_id` | `BIGINT` |
| `logos_resource_id` | `VARCHAR` |
| `logos_url` | `VARCHAR` |
| `publisher` | `VARCHAR` |
| `vote_count` | `BIGINT` |
| `best_commentaries_book_id` | `BIGINT` |
| `best_commentaries_url` | `VARCHAR` |
| `olivetree_id` | `BIGINT` |
| `olivetree_url` | `VARCHAR` |
| `abbreviation` | `VARCHAR` |
| `alternate_urls` | `VARCHAR[]` |
| `web_archive_url` | `VARCHAR` |
| `best_commentaries_series_id` | `VARCHAR` |
