FROM registry.fedoraproject.org/fedora:36
MAINTAINER "Jan Hutar" <jhutar@redhat.com>

RUN dnf -y install python3-boto3 python3-virtualenv python3-pip python3-psycopg2 python3-requests python3-psutil python3-pyyaml postgresql git-core dumb-init 'dnf-command(builddep)' \
    && dnf -y builddep python3-requests python3-psutil \
    && rm -rf /var/cache/yum/* /var/cache/dnf/*
RUN echo "Marker 2022-11-15 13:20" \
    && cd /home/ \
    && pip install -e 'git+https://github.com/redhat-performance/opl.git#egg=opl-rhcloud-perf-team' \
    && rm -rf /root/.cache/pip/wheels/

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["sleep", "infinity"]
