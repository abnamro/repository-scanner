import Config from '@/configuration/config';

const CommonUtils = {
  formatVcsProvider(vcsProvider) {
    let vcsProviderLabel;
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

  parseStatusOptions(statusOptions) {
    const statusList = [];
    statusOptions.forEach(function (value, index) {
      const statusJson = {};
      if (value === `${Config.value('notAnalyzedStatusVal')}`) {
        statusJson['id'] = index;
        statusJson['label'] = `${Config.value('notAnalyzedStatusLabel')}`;
        statusJson['value'] = value;
      } else if (value === `${Config.value('underReviewStatusVal')}`) {
        statusJson['id'] = index;
        statusJson['label'] = `${Config.value('underReviewStatusLabel')}`;
        statusJson['value'] = value;
      } else if (value === `${Config.value('clarificationRequiredStatusVal')}`) {
        statusJson['id'] = index;
        statusJson['label'] = `${Config.value('clarificationRequiredStatusLabel')}`;
        statusJson['value'] = value;
      } else if (value === `${Config.value('truePostiveStatusVal')}`) {
        statusJson['id'] = index;
        statusJson['label'] = `${Config.value('truePostiveStatusLabel')}`;
        statusJson['value'] = value;
      } else if (value === `${Config.value('falsePositiveStatusVal')}`) {
        statusJson['id'] = index;
        statusJson['label'] = `${Config.value('falsePositiveStatusLabel')}`;
        statusJson['value'] = value;
      }
      statusList.push(statusJson);
    });
    return statusList;
  },

  parseStatusLabels(input) {
    let status;
    if (input === `${Config.value('notAnalyzedStatusVal')}`) {
      status = `${Config.value('notAnalyzedStatusLabel')}`;
    } else if (input === `${Config.value('underReviewStatusVal')}`) {
      status = `${Config.value('underReviewStatusLabel')}`;
    } else if (input === `${Config.value('clarificationRequiredStatusVal')}`) {
      status = `${Config.value('clarificationRequiredStatusLabel')}`;
    } else if (input === `${Config.value('truePostiveStatusVal')}`) {
      status = `${Config.value('truePostiveStatusLabel')}`;
    } else if (input === `${Config.value('falsePositiveStatusVal')}`) {
      status = `${Config.value('falsePositiveStatusLabel')}`;
    }
    return status;
  },
};

export default CommonUtils;
