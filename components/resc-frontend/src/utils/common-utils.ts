import Config from '@/configuration/config';
import { type FindingStatus, type VCSProviders } from '@/services/shema-to-types';

export type StatusOptionType = {
  id: number;
  label: string;
  value: FindingStatus;
};

const CommonUtils = {
  formatVcsProvider(vcsProvider: VCSProviders): string {
    let vcsProviderLabel = '';
    switch (vcsProvider) {
      case `${Config.value('azureDevOpsVal')}`:
        vcsProviderLabel = `${Config.value('azureDevOpsLabel')}`;
        break;
      case `${Config.value('bitbucketVal')}`:
        vcsProviderLabel = `${Config.value('bitbucketLabel')}`;
        break;
      case `${Config.value('githubPublicVal')}`:
        vcsProviderLabel = `${Config.value('githubPublicLabel')}`;
        break;
    }
    return vcsProviderLabel;
  },

  parseStatusOptions(statusOptions: FindingStatus[]): StatusOptionType[] {
    const statusList = [] as StatusOptionType[];
    statusOptions.forEach(function (status, index) {
      const statusJson: StatusOptionType = {
        id: index,
        label: CommonUtils.formatStatusLabels(status),
        value: status,
      };
      statusList.push(statusJson);
    });
    return statusList;
  },

  formatStatusLabels(input: FindingStatus): string {
    if (input === `${Config.value('underReviewStatusVal')}`) {
      return `${Config.value('underReviewStatusLabel')}`;
    }
    if (input === `${Config.value('clarificationRequiredStatusVal')}`) {
      return `${Config.value('clarificationRequiredStatusLabel')}`;
    }
    if (input === `${Config.value('truePostiveStatusVal')}`) {
      return `${Config.value('truePostiveStatusLabel')}`;
    }
    if (input === `${Config.value('falsePositiveStatusVal')}`) {
      return `${Config.value('falsePositiveStatusLabel')}`;
    }
    return `${Config.value('notAnalyzedStatusLabel')}`;
  },
};

export function toRaw(
  input: string | null | number | undefined | string[] | number[],
): string | null | number | string[] | number[] {
  // We collapse undefined from any into null. undefined is not a valid Json type...
  return JSON.parse(JSON.stringify(input ?? null));
}

// export function toRawArray(input: string[] | number[]): string[] | number[] {
//   if (Symbol.iterator in Object(input)) {
//     // We collapse undefined from any into null. undefined is not a valid Json type...
//     // @ts-expect-error
//     return [...input].map((v: string | number) => toRaw(v));
//   }

//   return JSON.parse(JSON.stringify(input ?? null));
// }

export default CommonUtils;
