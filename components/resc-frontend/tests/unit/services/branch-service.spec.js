import BranchService from '@/services/branch-service';
import axios from 'axios';

jest.mock('axios');

describe('function getFindingsCountByStatusForBranch', () => {
  let branchInfoId = 1;
  let mocked_branchinfo_findings_metadata = {
    data: {
      branch_id: 'b1',
      branch_name: 'master',
      last_scanned_commit: 'dummy_commit',
      repository_info_id: 1,
      id_: 1,
    },
    true_positive: 1,
    false_positive: 2,
    not_analyzed: 3,
    under_review: 4,
    clarification_required: 5,
    total_findings_count: 15,
  };
  describe('when API call is successful for getFindingsCountByStatusForBranch', () => {
    it('should return branchinfo with findings metadata', async () => {
      axios.get.mockResolvedValueOnce(mocked_branchinfo_findings_metadata);

      const response = await BranchService.getFindingsCountByStatusForBranch(branchInfoId);
      expect(response).toEqual(mocked_branchinfo_findings_metadata);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.data.branch_id).toBe('b1');
      expect(response.data.branch_name).toBe('master');
      expect(response.data.last_scanned_commit).toBe('dummy_commit');
      expect(response.data.repository_info_id).toBe(1);
      expect(response.data.id_).toBe(1);
      expect(response.true_positive).toBe(1);
      expect(response.false_positive).toBe(2);
      expect(response.not_analyzed).toBe(3);
      expect(response.under_review).toBe(4);
      expect(response.clarification_required).toBe(5);
      expect(response.total_findings_count).toBe(15);
    });
  });

  describe('when API call fails', () => {
    it('should return error', async () => {
      axios.get.mockResolvedValueOnce([]);

      await BranchService.getFindingsCountByStatusForBranch('not_valid')
        .then((response) => {
          expect(response).toEqual([]);
          expect(response).not.toBeNull();
          expect(response.length).toBe(0);
        })
        .catch((error) => {
          expect(error).toBeDefined();
          expect(error).not.toBeNull();
        });
    });
  });
});
