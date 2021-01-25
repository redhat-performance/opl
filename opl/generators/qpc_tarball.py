import json
import logging
import os
import os.path
import tarfile
import tempfile

import boto3
import botocore.client

import opl.gen


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

        logging.debug(f"Going to upload {self.filename} to S3")
        s3_resource = boto3.resource(
            's3',
            aws_access_key_id=self.s3_conf['aws_access_key_id'],
            aws_secret_access_key=self.s3_conf['aws_secret_access_key'],
            region_name=self.s3_conf['aws_region'],
            config=botocore.config.Config(signature_version='s3v4'),
        )
        s3_bucket = s3_resource.Bucket(name=self.s3_conf['bucket'])
        s3_object = s3_bucket.Object(key=self.remotename)
        s3_object.upload_file(Filename=self.filename, ExtraArgs={'ServerSideEncryption': 'AES256'})
        self.download_url = s3_resource.meta.client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.s3_conf['bucket'],
                'Key': self.remotename,
            },
            ExpiresIn=3600 * 3,
        )
        self.size = s3_object.content_length
        logging.info(f"Uploaded {self.filename} with signed url {self.download_url}")

        os.remove(self.filename)

    def dump_manifest(self, dirname):
        filename = os.path.join(dirname, 'metadata.json')
        data = {
            "report_id": opl.gen.gen_uuid(),
            "host_inventory_api_version": "1.0",
            "source": "satellite",
            "source_metadata": {},
            "report_slices": {s.get_id(): {"number_hosts": s.get_host_count()} for s in self.slices},
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
        data = {
            "account": self.account,
            "category": "tar",
            "metadata": {
                "reporter": "",
                "stale_timestamp": "0001-01-01T00:00:00Z"
            },
            "request_id": self.remotename,
            "principal": self.account,
            "service": "qpc",
            "size": self.size,
            "url": self.download_url,
            "b64_identity": opl.gen.get_auth_header(self.account, self.account).decode('UTF-8'),
            "timestamp": opl.gen.gen_datetime().replace('+00:00', 'Z'),
        }
        return json.dumps(data)

    def __iter__(self):
        return self

    def __next__(self):
        if self.tarball_conf['count_slices'] == len(self.slices):
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
