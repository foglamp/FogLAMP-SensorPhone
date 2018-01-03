FILES=__init__.py sensor_phone.py

all: $(FOGLAMP_ROOT)/scripts updateDB
	mkdir $(FOGLAMP_ROOT)/python/foglamp/plugins/south/SensorPhone
	cp $(FILES) $(FOGLAMP_ROOT)/python/foglamp/plugins/south/SensorPhone

$(FOGLAMP_ROOT)/scripts:
	-echo The environment variable FOGLAMP_ROOT must be set
	@exit 1

install: updateDB
	mkdir /usr/local/foglamp/plugins/south/SensorPhone
	cp $(FILES) /usr/local/foglamp/plugins/south/SensorPhone

updateDB:
	psql < cmds.sql
