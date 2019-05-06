2. Edit the ``/etc/openstack_schedules/openstack_schedules.conf`` file and complete the following
   actions:

   * In the ``[database]`` section, configure database access:

     .. code-block:: ini

        [database]
        ...
        connection = mysql+pymysql://openstack_schedules:OPENSTACK_SCHEDULES_DBPASS@controller/openstack_schedules
