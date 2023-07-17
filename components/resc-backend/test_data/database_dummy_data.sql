INSERT INTO rule_allow_list (description, regexes, paths, commits, stop_words) VALUES
    ('global allow lists', NULL, 'gitleaks.toml', NULL, 'getenv,env_');

INSERT INTO rule_pack (version, global_allow_list, active) VALUES
    ('1.0.0', 1, 1);

INSERT INTO rules (rule_pack, allow_list, rule_name, description, entropy, secret_group, regex, [path], keywords) VALUES
    ('1.0.0', NULL, 'Google-OAuth-Access-Token', 'Google OAuth Access Token', NULL, NULL, 'ya29\\.[0-9A-Za-z\\-_]++', NULL, NULL),
    ('1.0.0', NULL, 'Github-Tokens', 'Github-Tokens', NULL, NULL, '(ghu|ghs|gho|ghp|ghr)_[0-9a-zA-Z]{36}', NULL, 'ghu_,ghs_,gho_,ghp_,ghr_');

INSERT INTO tag (name) VALUES
    ('Cli'),
    ('Warn');

INSERT INTO rule_tag (rule_id, tag_id) VALUES
    (1, 1),
    (2, 1);

INSERT INTO vcs_instance (name, provider_type, scheme, hostname, port, organization, vcs_scope, exceptions) VALUES
    ('AZURE_DEVOPS_ACCEPTANCE', 'AZURE_DEVOPS', 'https', 'fake-dev.azure.com', 443, 'ado-org', 'ado-project1,ado-project2', 'ado-project3'),
    ('BITBUCKET_DEV', 'BITBUCKET', 'https', 'fake-bitbucket.com', 443, NULL, NULL, NULL);

INSERT INTO repository (vcs_instance, project_key, repository_id, repository_name, repository_url) VALUES
   (1, 'ado-project1', 'r1', 'resc-dummy1', 'https://fake-dev.azure.com/ado-org/ado-project1/_git/resc-dummy1'),
   (1, 'ado-project2', 'r2', 'resc-dummy2', 'https://fake-dev.azure.com/ado-org/ado-project2/_git/resc-dummy2'),
   (2, 'btbk-project1', 'r3', 'resc-dummy3', 'https://fake-bitbucket.com/scm/r3/resc-dummy3.git');

INSERT INTO scan (rule_pack, scan_type, last_scanned_commit, [timestamp], increment_number, repository_id) VALUES
   ('1.0.0', 'BASE', 'qwerty1', '2023-07-14 00:00:00.000', 0, 1),
   ('1.0.0', 'INCREMENTAL', 'qwerty2', '2023-07-15 00:00:00.000', 1, 1),
   ('1.0.0', 'BASE', 'qwerty1', '2023-07-14 00:00:00.000', 0, 2),
   ('1.0.0', 'INCREMENTAL', 'qwerty2', '2023-07-15 00:00:00.000', 1, 2);

INSERT INTO finding (repository_id, rule_name, file_path, line_number, commit_id, commit_message, commit_timestamp, author, email, event_sent_on, column_start, column_end) VALUES
   (1, 'Google-OAuth-Access-Token', 'application.txt', 1, 'qwerty1', 'this is commit 1', '2023-01-01 00:00:00.000', 'developer', 'developer@abc.com', NULL, 1, 100),
   (1, 'Github-Tokens', 'application.txt', 2, 'qwerty1', 'this is commit 2', '2023-01-01 00:00:00.000', 'developer', 'developer@abc.com', NULL, 1, 80),
   (2, 'Google-OAuth-Access-Token', 'application.txt', 1, 'qwerty1', 'this is commit 1', '2023-01-01 00:00:00.000', 'developer', 'developer@abc.com', NULL, 1, 100),
   (2, 'Github-Tokens', 'application.txt', 2, 'qwerty1', 'this is commit 2', '2023-01-01 00:00:00.000', 'developer', 'developer@abc.com', NULL, 1, 80),
   (3, 'Google-OAuth-Access-Token', 'application.txt', 1, 'qwerty1', 'this is commit 1', '2023-01-01 00:00:00.000', 'developer', 'developer@abc.com', NULL, 1, 100),
   (3, 'Github-Tokens', 'application.txt', 2, 'qwerty1', 'this is commit 2', '2023-01-01 00:00:00.000', 'developer', 'developer@abc.com', NULL, 1, 80);

INSERT INTO scan_finding(scan_id, finding_id) VALUES
   (1, 1),
   (1, 2),
   (1, 3),
   (1, 4),
   (1, 5),
   (1, 6);

INSERT INTO audit(finding_id, [status], auditor, comment, [timestamp]) VALUES
   (1, 'NOT_ANALYZED', 'Anonymous', NULL, '2023-07-20 00:00:00.000'),
   (1, 'TRUE_POSITIVE', 'Anonymous', 'It is a true positive issue', '2023-07-21 00:00:00.000');