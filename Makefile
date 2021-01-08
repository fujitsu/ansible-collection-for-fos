test:
	@python3 tests/local_unit/test_fos_command.py
	@python3 tests/local_unit/test_fos_facts.py
	@python3 tests/local_unit/test_fos_config.py
	@python3 tests/local_unit/test_fos_vlan.py

copy:
	@mkdir -p ~/.ansible/collections/ansible_collections/fujitsu/fos/
	@cp -r plugins/ ~/.ansible/
	@cp -r plugins/ ~/.ansible/collections/ansible_collections/fujitsu/fos/
