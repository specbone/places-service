CREATE OR REPLACE VIEW vTasks AS
SELECT
	t.name		as task,
	s.value		as status,
	s.name		as name,
	t.started 	as last_started
FROM service.tasks t
JOIN service.status s ON s.uid = t.status_id;

CREATE OR REPLACE VIEW vPlaces AS
SELECT
 country.name 			as country,
 country.common_name 	as country2,
 country.code 			as country_code,
 state.name 			as state,
 state.code 			as state_code,
 county.name 			as county,
 county.code 			as county_code,
 city.name				as city,
 city.code				as city_code
FROM service.countries country
INNER JOIN service.states state ON state.country_id = country.uid
INNER JOIN service.counties county ON county.state_id = state.uid
INNER JOIN service.cities city ON city.county_id = county.uid;