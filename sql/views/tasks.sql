CREATE OR REPLACE VIEW vTasks AS
SELECT
	t.name		as task,
	s.value		as status,
	s.name		as name,
	t.started 	as last_started
FROM service.tasks t
JOIN service.status s ON s.uid = t.status_id;