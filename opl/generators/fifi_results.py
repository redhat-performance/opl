import logging

import opl.gen


class PlaybookRunMessageGenerator:
    def __init__(self, runs=1, nodes=1, hosts=1, duration=1, console=1, diff_mode=True):
        assert runs >= 1   # how many playbooks to run
        self.runs = runs
        assert nodes >= 1   # how many nodes should there be per run
        self.nodes = nodes
        assert hosts >= 1   # how many hosts should there be per node
        self.hosts = hosts
        assert duration >= 1   # how many run updates to send per run per node
        assert console >= 1   # how big should console output be (last char is newline)
        self.diff_mode = diff_mode   # console update is aditive, or total
        logging.debug(f"Created generator with runs = {runs}; nodes = {nodes}; duration = {duration}; console = {console}; diff_mode = {diff_mode}")

        self.index = -runs   # what message are we sending? (-number means start messages)

        self.objects = {
            'runs': [],
        }
        for run_id in range(runs):
            run = {
                'playbook_run_id': opl.gen.gen_uuid(),
                'account': '1212729',
                'serial': 0,
                'started': False,
                'nodes': [],
            }
            for node_id in range(nodes):
                node = {
                    'in_response_to': opl.gen.gen_uuid(),
                    'sender': opl.gen.gen_uuid(),
                    'hosts': [],
                }
                for host_id in range(hosts):
                    host = {
                        'host': opl.gen.gen_hostname(),
                        'sequence': 0,
                        'duration': duration,
                        'size': console,
                        'finished': False,
                        'console': '',
                    }
                    node['hosts'].append(host)
                run['nodes'].append(node)
            self.objects['runs'].append(run)

        logging.debug(f"Prepared {self.objects}")

    def seed_db(self, db, queries):
        """
        Create required rows in remediations DB so messages we are going to
        emit can be recorded to the DB
        """
        cursor = db.cursor()
        for run in self.objects['runs']:
            remediations__id = opl.gen.gen_uuid()
            sql = queries['seed_remediations']
            logging.debug(f"{sql} {remediations__id}")
            cursor.execute(sql, (
                remediations__id,
                'perf test playbook',
                run['account'],
                'tester',
                'tester',
            ))
            playbook_runs__id = run['playbook_run_id']
            sql = queries['seed_playbook_runs']
            logging.debug(f"{sql} {playbook_runs__id}")
            cursor.execute(sql, (
                playbook_runs__id,
                remediations__id,
                'tester',
            ))
            for node in run['nodes']:
                playbook_run_executors__id = opl.gen.gen_uuid()
                sql = queries['seed_playbook_run_executors']
                logging.debug(f"{sql} {playbook_run_executors__id}")
                cursor.execute(sql, (
                    playbook_run_executors__id,
                    opl.gen.gen_uuid(),
                    opl.gen.gen_hostname(),
                    node['sender'],
                    node['in_response_to'],
                    '---',
                    playbook_runs__id,
                    not self.diff_mode,
                ))
                for host in node['hosts']:
                    sql = queries['seed_playbook_run_systems']
                    logging.debug(f"{sql} {host['host']}")
                    cursor.execute(sql, (
                        opl.gen.gen_uuid(),
                        opl.gen.gen_uuid(),
                        host['host'],
                        playbook_run_executors__id,
                    ))
        db.commit()
        cursor.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < 0:
            run_id = self.index + self.runs
            node_id = 0
            host_id = 0
        else:
            # We want this logic so all hosts will be used - example for
            # runs=2, nodes=3 and hosts=4:
            #
            # index | run_id | node_id | host_id
            # ------+--------+---------+--------
            #     0 |      0 |       0 |       0
            #     1 |      1 |       0 |       0
            #     2 |      0 |       1 |       0
            #     3 |      1 |       1 |       0
            #     4 |      0 |       2 |       0
            #     5 |      1 |       2 |       0
            #     6 |      0 |       0 |       1
            #     7 |      1 |       0 |       1
            #     8 |      0 |       1 |       1
            #
            # and so on
            run_id = self.index % self.runs
            node_id = int((float(self.index) / self.runs) % self.nodes)
            host_id = int((float(self.index) / (self.runs * self.nodes)) % self.hosts)

        playbook_run_id = self.objects['runs'][run_id]['playbook_run_id']
        account =         self.objects['runs'][run_id]['account']   # noqa: E222
        started =         self.objects['runs'][run_id]['started']   # noqa: E222
        serial =          self.objects['runs'][run_id]['serial']   # noqa: E222
        in_response_to =  self.objects['runs'][run_id]['nodes'][node_id]['in_response_to']   # noqa: E222
        sender =          self.objects['runs'][run_id]['nodes'][node_id]['sender']   # noqa: E222
        host =            self.objects['runs'][run_id]['nodes'][node_id]['hosts'][host_id]['host']   # noqa: E222
        sequence =        self.objects['runs'][run_id]['nodes'][node_id]['hosts'][host_id]['sequence']   # noqa: E222
        size =            self.objects['runs'][run_id]['nodes'][node_id]['hosts'][host_id]['size']   # noqa: E222
        duration =        self.objects['runs'][run_id]['nodes'][node_id]['hosts'][host_id]['duration']   # noqa: E222
        finished =        self.objects['runs'][run_id]['nodes'][node_id]['hosts'][host_id]['finished']   # noqa: E222

        logging.debug(f"Generating message index = {self.index}; run_id = {run_id}; node_id = {node_id}; host_id = {host_id}; serial = {serial}; sequence = {sequence}; duration = {duration}; started = {started}; finished = {finished}")

        if sequence > duration:
            # End of game
            raise StopIteration()

        if not started:
            # This is starting message
            logging.debug(f"START message {self.index} for run_id = {run_id}")
            self.index += 1
            self.objects['runs'][run_id]['started'] = True
            return {
                'account': account,
                'code': 0,
                'in_response_to': in_response_to,
                'message_id': opl.gen.gen_uuid(),
                'message_type': 'response',
                'payload': {
                    'playbook_run_id': playbook_run_id,
                    'type': 'playbook_run_ack',
                },
                'sender': sender,
                'serial': 1,
            }

        if sequence == duration and not finished:
            # This is final message
            logging.debug(f"FINAL message {self.index} for run_id = {run_id}; node_id = {node_id}; host_id = {host_id}")
            self.index += 1
            self.objects['runs'][run_id]['serial'] += 1
            self.objects['runs'][run_id]['nodes'][node_id]['hosts'][host_id]['sequence'] += 1
            self.objects['runs'][run_id]['nodes'][node_id]['hosts'][host_id]['finished'] = True
            return {
                'account': account,
                'code': 0,
                'in_response_to': in_response_to,
                'message_id': opl.gen.gen_uuid(),
                'message_type': 'response',
                'payload': {
                    'host': host,
                    'playbook_run_id': playbook_run_id,
                    'status': 'success',
                    'type': 'playbook_run_finished',
                },
                'sender': sender,
                'serial': serial,
            }
        elif sequence == duration and finished:
            # This message seqence was already finished
            self.index += 1
            pass
        else:
            # This is normal progress message
            logging.debug(f"Normal message {self.index} for run_id = {run_id}; node_id = {node_id}; host_id = {host_id}")
            self.index += 1
            self.objects['runs'][run_id]['serial'] += 1
            self.objects['runs'][run_id]['nodes'][node_id]['hosts'][host_id]['sequence'] += 1

            # Determine console content
            if self.diff_mode:
                self.objects['runs'][run_id]['nodes'][node_id]['hosts'][host_id]['console'] = opl.gen.gen_string(size=size-1) + '\n'
            else:
                self.objects['runs'][run_id]['nodes'][node_id]['hosts'][host_id]['console'] += opl.gen.gen_string(size=size-1) + '\n'
            console = self.objects['runs'][run_id]['nodes'][node_id]['hosts'][host_id]['console']

            return {
                'account': account,
                'code': 0,
                'in_response_to': in_response_to,
                'message_id': opl.gen.gen_uuid(),
                'message_type': 'response',
                'payload': {
                    'console': console,
                    'host': host,
                    'playbook_run_id': playbook_run_id,
                    'sequence': sequence,
                    'type': 'playbook_run_update',
                },
                'sender': sender,
                'serial': serial,
            }
