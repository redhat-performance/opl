OPL generators
==============

This directory contains bunch of classes that generate some random
data based on some template and other input.


`fifi_results.py`: `PlaybookRunMessageGenerator`
------------------------------------------------

This is very specific for Remediations service.

Right now I can not recall on how does this work and what it is for :-)


`inventory_egress.py`: `EgressHostsGenerator`
---------------------------------------------

This was used in Patchman tests to generate `platform.inventory.events`
messages (HBI output messages).


`inventory_ingress.py`: `InventoryIngressGenerator`
---------------------------------------------------

Used to generate HBI input messages, but with correct template it
can generate various things. Please check existing templates:

 * `opl/generators/inventory_ingress_InvGitUtilsPayload_template.json.j2` -
    template based on HBI git example file for usual HBI input message
 * `opl/generators/inventory_ingress_RHSM_template.json.j2` - template
   for RHSM Conduit messages
 * `opl/generators/inventory_ingress_yupana_template.json.j2` - template
   used in `QPCTarballGenerator` for yupana host records

When you iterate through the generator, it return's `count` of touples
with random `subscription_manager_id` and dict with full message.

Example usage:

    >>> import opl.generators.inventory_ingress
    >>> generator = opl.generators.inventory_ingress.InventoryIngressGenerator(count=3, template='inventory_ingress_RHSM_template.json.j2')
    >>> for msg_id, msg_struct in generator:
    ...   print(f"Message {msg_id}: {str(msg_struct)[:50]}")
    ... 
    Message 30eddf6c-9537-4501-8215-1a45f8ed4e73: {'operation': 'add_host', 'data': {'account': '025
    Message e29b590d-3f07-41fc-aaf2-4ce32d989f6f: {'operation': 'add_host', 'data': {'account': '012
    Message 2980c74a-4876-4ef5-b277-3bdca3655f48: {'operation': 'add_host', 'data': {'account': '064


`packages.py`: `PackagesGenerator`
----------------------------------

Returns set of random packages with given size. Packages are picked
from data file so requested amount of packages can not be higher of
what we have in the data file.

Example usage:

    >>> import opl.generators.packages
    >>> generator = opl.generators.packages.PackagesGenerator()
    >>> print(f"Choosing from {generator.count()} packages")
    Choosing from 4163 packages
    >>> print(f"Example set with 3 packages: {generator.generate(3)}")
    Example set with 3 packages: ['libsoup-0:2.48.1-3.el7.i686', 'openssl-libs-1:1.0.1e-51.el7_2.5.x86_64', 'texlive-ncntrsbk-2:svn28614.0-32.el7.noarch']
    >>> print(f"Example set with 3 packages: {generator.generate(3)}")
    Example set with 3 packages: ['xml-commons-resolver-0:1.2-15.el7.noarch', 'foomatic-filters-0:4.0.9-6.el7.x86_64', 'boost-date-time-0:1.53.0-25.el7.x86_64']

`qpc_tarball.py`: `QPCTarballGenerator`
---------------------------------------

Generate QPC (Yupana) tarballs with given number of slices and so.

Example usage:

    s3_conf = {
        'aws_access_key_id': args.s3_aws_access_key_id,
        'aws_region': args.s3_aws_region,
        'aws_secret_access_key': args.s3_aws_secret_access_key,
        'bucket': args.s3_bucket,
        'endpoint': args.s3_endpoint,
    }
    tarball_conf = {
        'tarballs_count': args.tarballs_count,
        'slices_count': args.slices_count,
        'hosts_count': args.hosts_count,
        'hosts_template': args.hosts_template,
        'hosts_packages': args.hosts_packages,
    }
    
    tarball_generator = opl.generators.qpc_tarball.QPCTarballGenerator(
        count=args.tarballs_count, tarball_conf=tarball_conf, s3_conf=s3_conf)
    
    for tarball in tarball_generator:
        for tarball_slice in tarball:
            host_generator = opl.generators.inventory_ingress.InventoryIngressGenerator(...)
            
            for host_id, host_data in host_generator:
                host_data = host_data["data"]
                tarball_slice.add_host(host_data)
        
        tarball.upload()

