import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import Config from '@/configuration/config';
import ScanFindingsService from '@/services/scan-findings-service';
import scans_for_a_repository from '@/../tests/resources/mock_scans_for_a_repository.json';
import repositories from '@/../tests/resources/mock_repositories.json';

vi.mock('axios');

describe('getRepositoryById', () => {
  describe('when API call is successful', () => {
    it('should return repositories', async () => {
      axios.get.mockResolvedValueOnce(repositories);

      const response = await ScanFindingsService.getRepositoryById(1);

      expect(response).toEqual(repositories);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.data.length).toBe(2);
      expect(response.total).toBe(100);
      expect(response.limit).toBe(2);
      expect(response.skip).toBe(0);
    });
  });

  describe('getScanById', () => {
    describe('when API call is successful', () => {
      it('should return scans', async () => {
        const scan = {
          scan_type: 'BASE',
          last_scanned_commit: '1fb42a9ee177ed8141a4ab162a3e33952a4cf6c0',
          timestamp: '2023-05-23T15:52:22.270000',
          increment_number: 0,
          rule_pack: '1.0.0',
          repository_id: 1,
          id_: 1,
        };
        axios.get.mockResolvedValueOnce(scan);

        const response = await ScanFindingsService.getScanById(1);

        expect(response).toEqual(scan);
        expect(response).toBeDefined();
        expect(response.scan_type).toBe('BASE');
        expect(response.last_scanned_commit).toBe('1fb42a9ee177ed8141a4ab162a3e33952a4cf6c0');
        expect(response.timestamp).toBe('2023-05-23T15:52:22.270000');
        expect(response.increment_number).toBe(0);
        expect(response.rule_pack).toBe('1.0.0');
        expect(response.repository_id).toBe(1);
        expect(response.id_).toBe(1);
      });
    });

    describe('when API call fails', () => {
      it('should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await ScanFindingsService.getScanById('not_valid')
          .then((response) => {
            expect(response).toEqual([]);
            expect(response).not.toBeNull();
          })
          .catch((error) => {
            expect(error).toBeDefined();
            expect(error).not.toBeNull();
          });
      });
    });
  });

  describe('getScansByRepositoryId', () => {
    describe('when API call is successful', () => {
      it('should return scans', async () => {
        axios.get.mockResolvedValueOnce(scans_for_a_repository);

        const response = await ScanFindingsService.getScansByRepositoryId(1, 0, 100);

        expect(response).toEqual(scans_for_a_repository);
        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.data.length).toBe(2);
        expect(response.data[0].scan_type).toBe('BASE');
        expect(response.data[0].last_scanned_commit).toBe(
          '5af6e79b1a9a1484ae3946a7e2c8d05febfe2c63',
        );
        expect(response.data[0].timestamp).toBe('2023-04-30T06:01:47.503000');
        expect(response.data[0].increment_number).toBe(0);
        expect(response.data[0].rule_pack).toBe('1.0.0');
        expect(response.data[0].repository_id).toBe(1);
        expect(response.data[0].id_).toBe(1);
      });
    });

    describe('when API call fails', () => {
      it('should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await ScanFindingsService.getScansByRepositoryId('not_valid', 0, 100)
          .then((response) => {
            expect(response).toEqual([]);
            expect(response).not.toBeNull();
          })
          .catch((error) => {
            expect(error).toBeDefined();
            expect(error).not.toBeNull();
          });
      });
    });
  });

  describe('getStatusList', () => {
    let mock_statuses = [
      `${Config.value('notAnalyzedStatusVal')}`,
      `${Config.value('underReviewStatusVal')}`,
      `${Config.value('clarificationRequiredStatusVal')}`,
      `${Config.value('falsePositiveStatusVal')}`,
      `${Config.value('truePostiveStatusVal')}`,
    ];
    describe('when API call is successful', () => {
      it('should return statuses', async () => {
        axios.get.mockResolvedValueOnce(mock_statuses);

        const response = await ScanFindingsService.getStatusList();

        expect(response).toEqual(mock_statuses);
        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.length).toBe(5);
      });
    });

    describe('when API call fails', () => {
      it('should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await ScanFindingsService.getStatusList('not valid')
          .then((response) => {
            expect(response).toEqual([]);
            expect(response).not.toBeNull();
            expect(response.data.length).toBe(0);
          })
          .catch((error) => {
            expect(error).toBeDefined();
            expect(error).not.toBeNull();
          });
      });
    });
  });

  describe('getRulesByScanIds', () => {
    let mock_rules = [
      'Azure-Token',
      'Environment-configuration-file',
      'File-extensions-with-keys-and-credentials',
    ];
    describe('when API call is successful', () => {
      it('should return rules', async () => {
        axios.get.mockResolvedValueOnce(mock_rules);

        const response = await ScanFindingsService.getRulesByScanIds([1, 2]);

        expect(response).toEqual(mock_rules);
        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.length).toBe(3);
      });
    });

    describe('when API call fails', () => {
      it('should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await ScanFindingsService.getRulesByScanIds('not valid')
          .then((response) => {
            expect(response).toEqual([]);
            expect(response).not.toBeNull();
            expect(response.data.length).toBe(0);
          })
          .catch((error) => {
            expect(error).toBeDefined();
            expect(error).not.toBeNull();
          });
      });
    });
  });
});
