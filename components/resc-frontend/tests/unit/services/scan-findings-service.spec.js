import axios from 'axios';
import ScanFindingsService from '@/services/scan-findings-service';
import scans from '@/../tests/resources/mock_scans.json';
import branches from '@/../tests/resources/mock_branches.json';
import repositories from '@/../tests/resources/mock_repositories.json';

jest.mock('axios');

describe('getRepositoryInfoById', () => {
  describe('when API call is successful', () => {
    it('should return repositories', async () => {
      axios.get.mockResolvedValueOnce(repositories);

      const response = await ScanFindingsService.getRepositoryInfoById(1);

      expect(response).toEqual(repositories);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.data.length).toBe(2);
      expect(response.total).toBe(100);
      expect(response.limit).toBe(2);
      expect(response.skip).toBe(0);
    });
  });

  describe('getScanInfoById', () => {
    describe('when API call is successful', () => {
      it('should return scans', async () => {
        axios.get.mockResolvedValueOnce(scans);

        const response = await ScanFindingsService.getScanInfoById(1);

        expect(response).toEqual(scans);
        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.data.length).toBe(5);
        expect(response.total).toBe(100);
        expect(response.limit).toBe(5);
        expect(response.skip).toBe(0);
      });
    });

    describe('when API call fails', () => {
      it('should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await ScanFindingsService.getScanInfoById('not_valid')
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

  describe('getBranchInfoById', () => {
    describe('when API call is successful', () => {
      it('should return branches', async () => {
        axios.get.mockResolvedValueOnce(branches);

        const response = await ScanFindingsService.getBranchInfoById(1);

        expect(response).toEqual(branches);
        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.data.length).toBe(2);
        expect(response.total).toBe(200);
        expect(response.limit).toBe(2);
        expect(response.skip).toBe(0);
      });
    });

    describe('when API call fails', () => {
      it('should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await ScanFindingsService.getBranchInfoById('not_valid')
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

  describe('getRulesByScanId', () => {
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

  describe('getStatusList', () => {
    let mock_statuses = [
      'NOT_ANALYZED',
      'UNDER_REVIEW',
      'CLARIFICATION_REQUIRED',
      'FALSE_POSITIVE',
      'TRUE_POSITIVE',
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

  describe('getScansByBranchId', () => {
    describe('when API call is successful', () => {
      it('should return scans', async () => {
        axios.get.mockResolvedValueOnce(scans);

        const response = await ScanFindingsService.getScansByBranchId(1);

        expect(response).toEqual(scans);
        expect(response).toBeDefined();
        expect(response).not.toBeNull();
        expect(response.data.length).toBe(5);
        expect(response.total).toBe(100);
        expect(response.limit).toBe(5);
        expect(response.skip).toBe(0);
      });
    });

    describe('when API call fails', () => {
      it('should return error', async () => {
        axios.get.mockResolvedValueOnce([]);

        await ScanFindingsService.getScansByBranchId('not_valid')
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

  describe('parseStatusOptions', () => {
    it('should parse status options', async () => {
      let statusOptions = [
        'NOT_ANALYZED',
        'UNDER_REVIEW',
        'CLARIFICATION_REQUIRED',
        'FALSE_POSITIVE',
        'TRUE_POSITIVE',
      ];
      const statusList = ScanFindingsService.parseStatusOptions(statusOptions);

      expect(statusList).toBeDefined();
      expect(statusList).not.toBeNull();
      expect(statusList.length).toBe(5);
      expect(statusList[0].label).toBe('Not Analyzed');
      expect(statusList[1].label).toBe('Under Review');
      expect(statusList[2].label).toBe('Clarification Required');
      expect(statusList[3].label).toBe('False Positive');
      expect(statusList[4].label).toBe('True Positive');
    });
  });
});
