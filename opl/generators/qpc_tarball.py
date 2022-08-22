import json
import logging
import os
import os.path
import tarfile
import tempfile

import opl.gen
import opl.s3_tools


def get_tarball_message(account, remotename, size, download_url):
    data = {
        "account": account,
        "org_id": account,
        "category": "tar",
        "metadata": {
            "reporter": "",
            "stale_timestamp": "0001-01-01T00:00:00Z"
        },
        "request_id": remotename[-45:],
        "principal": account,
        "service": "qpc",
        "size": size,
        "url": download_url,
        "b64_identity": opl.gen.get_auth_header(account, account).decode('UTF-8'),
        "timestamp": opl.gen.gen_datetime().replace('+00:00', 'Z'),
    }
    return json.dumps(data)


class QPCTarballSlice:
    """QPC Tarball slice creator class"""

    def __init__(self):
        self.id = opl.gen.gen_uuid()
        self.hosts = []

    def get_id(self):
        return self.id

    def get_host_count(self):
        return len(self.hosts)

    def add_host(self, host_json):
        self.hosts.append(host_json)

    def dump(self, dirname):
        filename = os.path.join(dirname, self.id + ".json")
        logging.debug(f"Writing {filename}")
        with open(filename, "w") as fp:
            json.dump({"report_slice_id": self.id, "hosts": self.hosts}, fp)

        return self.id + '.json'


class QPCTarball:
    """QPC Tarball creator class"""

    def __init__(self, tarball_conf, s3_conf=None):
        self.slices = []
        self.filename = tempfile.mkstemp(suffix='-output.tar.gz')[1]
        self.remotename = os.path.join('upload-service-opl', os.path.basename(self.filename))
        self.s3_conf = s3_conf
        self.tarball_conf = tarball_conf
        self.download_url = None
        self.size = None
        self.account = opl.gen.gen_account()

    def upload(self):
        self.dump()

        s3_resource = opl.s3_tools.connect(self.s3_conf)
        self.size = opl.s3_tools.upload_file(s3_resource, self.filename, self.s3_conf['bucket'], self.remotename)
        self.download_url = opl.s3_tools.get_presigned_url(s3_resource, self.s3_conf['bucket'], self.remotename)

        os.remove(self.filename)

    def dump_manifest(self, dirname):
        filename = os.path.join(dirname, 'metadata.json')
        data = {
            "report_id": opl.gen.gen_uuid(),
            "host_inventory_api_version": "1.0",
            "source": "Satellite",
            "source_metadata": {
                "foreman_rh_cloud_version": "3.0.14",
            },
            "report_slices": {
                s.get_id(): {"number_hosts": s.get_host_count()} for s in self.slices
            },
        }

        logging.debug(f"Writing {filename}")
        with open(filename, "w") as fp:
            json.dump(data, fp)

        return 'metadata.json'

    def dump(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            files = []

            for s in self.slices:
                files.append(s.dump(tmpdirname))

            files.append(self.dump_manifest(tmpdirname))

            orig_cwd = os.getcwd()
            os.chdir(tmpdirname)
            tar = tarfile.open(self.filename, "w:gz")
            for name in files:
                tar.add(name)
            tar.close()
            os.chdir(orig_cwd)

            logging.info(f"Wrote {self.filename}")

            return self.filename

    def dumps_message(self):
        return get_tarball_message(self.account, self.remotename, self.size, self.download_url)

    def __iter__(self):
        return self

    def __next__(self):
        if self.tarball_conf['slices_count'] == len(self.slices):
            raise StopIteration()

        new_slice = QPCTarballSlice()
        self.slices.append(new_slice)
        return new_slice


class QPCTarballGenerator:
    """Iterator that creates QPC tarball objects"""

    def __init__(self, count, tarball_conf, s3_conf=None):
        self.counter = 0
        self.count = count   # how many tarballs to produce
        self.tarball_conf = tarball_conf
        self.s3_conf = s3_conf

    def __iter__(self):
        return self

    def __next__(self):
        if self.counter == self.count:
            raise StopIteration()

        self.counter += 1
        return QPCTarball(tarball_conf=self.tarball_conf, s3_conf=self.s3_conf)
