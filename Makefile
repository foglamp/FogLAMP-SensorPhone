FILES=__init__.py sensor_phone.py

all: $(FOGLAMP_ROOT)/scripts updateDB
	mkdir $(FOGLAMP_ROOT)/python/foglamp/plugins/south/sensor_phone
	cp $(FILES) $(FOGLAMP_ROOT)/python/foglamp/plugins/south/sensor_phone

$(FOGLAMP_ROOT)/scripts:
	-echo The environment variable FOGLAMP_ROOT must be set
	@exit 1

install: updateDB
	mkdir /usr/local/foglamp/plugins/south/sensor_phone
	cp $(FILES) /usr/local/foglamp/plugins/south/sensor_phone

updateDB:
	psql < cmds.sql
