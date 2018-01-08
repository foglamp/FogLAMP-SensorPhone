--- Database commands to insert the new plugin into FogLAMP

--- Create the south service instannce
INSERT INTO foglamp.scheduled_processes ( name, script ) VALUES ( 'SensorApp', '["services/south"]');

--- Add the schedule to start the service at system startup
INSERT INTO foglamp.schedules ( id, schedule_name, process_name, schedule_type,schedule_interval, exclusive )
     VALUES ( '543a59ce-a9ca-11e7-abc4-cec278b6b11a', 'SensorPhone', 'SensorApp', 1, '0:0', true );

--- Insert the config needed to load the plugin
INSERT INTO foglamp.configuration ( key, description, value )
     VALUES ( 'SensorApp', 'SensorPhone App on iPhone',
	      '{"plugin" : { "type" : "string", "value" : "SensorPhone", "default" : "SensorPhone", "description" : "Plugin to load" } }' );

