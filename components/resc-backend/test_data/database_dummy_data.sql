INSERT INTO vcs_instance (name, provider_type, scheme, hostname, port, organization, vcs_scope, exceptions) VALUES
    ('bitbucket server', 'BITBUCKET', 'https', 'fake-host.com', 443, NULL, NULL, NULL),
    ('ado scope 1', 'AZURE_DEVOPS', 'https', 'fake-host.com', 443, 'space-org', 'proj1,proj2', '');

INSERT INTO repository ( project_key, repository_id, repository_name, repository_url, vcs_instance) VALUES
    ( 'ado-proj1', 'r1', 'repo1', 'https://fake-ado.com/p1/r1', 1),
    ( 'ado-proj1', 'r2', 'repo1', 'https://fake-ado.com/p1/r2', 1),
    ( 'ado-proj2', 'r1', 'repo1', 'https://fake-ado.com/p2/r1', 1),
    ( 'btbk-proj1', 'r1', 'repo1', 'https://fake-bitbucket.com/p1/r1', 2);

INSERT INTO branch ( repository_id, branch_id, branch_name, latest_commit) VALUES
    ( 1, 'b1', 'branch1', 'qwerty123'),
    ( 1, 'b2', 'branch2', 'qwerty123'),
    ( 3, 'b1', 'branch1', 'qwerty123'),
    ( 4, 'b1', 'branch1', 'qwerty123');


INSERT INTO rule_allow_list (description) VALUES
    ('rule allow list number 1');

INSERT INTO rule_pack (version, global_allow_list, active) VALUES
    ('0.0.0', 1, 1);

INSERT INTO rules (rule_pack, rule_name, description, regex) VALUES
    ('0.0.0', 'rule#1', 'rule number 1', '*.*'),
    ('0.0.0', 'rule#2', 'rule number 2', '*.*');

INSERT INTO scan (branch_id, [timestamp], scan_type, last_scanned_commit, increment_number, rule_pack) VALUES
    (1, '2021-01-01 00:00:00.000', 'BASE', 'qwerty1', 0, '0.0.0'),
    (2, '2020-01-01 00:00:00.000', 'BASE', 'qwerty1', 0, '0.0.0'),
    (3, '2022-02-24 17:00:00.000', 'BASE', 'qwerty1', 0, '0.0.0'),
    (3, '2022-03-24 17:00:00.000', 'BASE', 'qwerty1', 0, '0.0.0');

INSERT INTO finding (branch_id, file_path, line_number, commit_id, commit_message, commit_timestamp, author, email, rule_name, column_start, column_end) VALUES
    (1, '/path/to/file', 123, 'qwerty1', 'this is commit 1', '2021-01-01 00:00:00.000', 'developer', 'developer@abn.com', 'rule#1', 1, 100),
    (1, '/path/to/file', 123, 'qwerty1', 'this is commit 1', '2021-01-01 00:00:00.000', 'developer', 'developer@abn.com', 'rule#2', 0, 0),
    (2, '/path/to/file', 123, 'qwerty1', 'this is commit 1', '2021-01-01 00:00:00.000', 'developer', 'developer@abn.com', 'rule#1', 1, 50),
    (2, '/path/to/file', 123, 'qwerty1', 'this is commit 1', '2021-01-01 00:00:00.000', 'developer', 'developer@abn.com', 'rule#2', 42, 43),
    (3, '/path/to/file', 123, 'qwerty1', 'this is commit 1', '2021-01-01 00:00:00.000', 'developer', 'developer@abn.com', 'rule#1', 12, 34),
    (3, '/path/to/file', 123, 'qwerty1', 'this is commit 1', '2021-01-01 00:00:00.000', 'developer', 'developer@abn.com', 'rule#2', 21, 34),
    (3, '/path/to/file', 123, 'qwerty2', 'this is commit 2', '2021-01-01 00:00:00.000', 'developer', 'developer@abn.com', 'rule#1', 12, 34);

INSERT INTO scan_finding(scan_id, finding_id) VALUES
    (1, 1),
    (1, 2),
    (2, 3),
    (2, 4),
    (3, 5),
    (3, 6),
    (4, 6),
    (4, 7);

INSERT INTO audit(finding_id, status, auditor, comment, [timestamp]) VALUES
    (1, 'NOT_ANALYZED', 'Anonymous', NULL, '2023-01-01 00:00:00.000'),
    (1, 'TRUE_POSITIVE', 'Anonymous', 'It is a true positive issue', '2023-01-02 00:00:00.000')