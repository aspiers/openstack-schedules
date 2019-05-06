Prerequisites
-------------

Before you install and configure the event scheduling service,
you must create a database, service credentials, and API endpoints.

#. To create the database, complete these steps:

   * Use the database access client to connect to the database
     server as the ``root`` user:

     .. code-block:: console

        $ mysql -u root -p

   * Create the ``openstack_schedules`` database:

     .. code-block:: none

        CREATE DATABASE openstack_schedules;

   * Grant proper access to the ``openstack_schedules`` database:

     .. code-block:: none

        GRANT ALL PRIVILEGES ON openstack_schedules.* TO 'openstack_schedules'@'localhost' \
          IDENTIFIED BY 'OPENSTACK_SCHEDULES_DBPASS';
        GRANT ALL PRIVILEGES ON openstack_schedules.* TO 'openstack_schedules'@'%' \
          IDENTIFIED BY 'OPENSTACK_SCHEDULES_DBPASS';

     Replace ``OPENSTACK_SCHEDULES_DBPASS`` with a suitable password.

   * Exit the database access client.

     .. code-block:: none

        exit;

#. Source the ``admin`` credentials to gain access to
   admin-only CLI commands:

   .. code-block:: console

      $ . admin-openrc

#. To create the service credentials, complete these steps:

   * Create the ``openstack_schedules`` user:

     .. code-block:: console

        $ openstack user create --domain default --password-prompt openstack_schedules

   * Add the ``admin`` role to the ``openstack_schedules`` user:

     .. code-block:: console

        $ openstack role add --project service --user openstack_schedules admin

   * Create the openstack_schedules service entities:

     .. code-block:: console

        $ openstack service create --name openstack_schedules --description "event scheduling" event scheduling

#. Create the event scheduling service API endpoints:

   .. code-block:: console

      $ openstack endpoint create --region RegionOne \
        event scheduling public http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        event scheduling internal http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        event scheduling admin http://controller:XXXX/vY/%\(tenant_id\)s
