<template>
  <div class="row">
    <table class="table table-sm table-borderless">
      <tbody>
        <tr>
          <th>Project</th>
          <td>
            <span class="badge badge-color">{{ repositoryInfo.project_key }}</span>
          </td>
        </tr>
        <tr>
          <th>Repository</th>
          <td>
            <span class="badge badge-color">{{ repositoryInfo.repository_name }}</span>
          </td>
        </tr>
        <tr>
          <th>VCS Instance</th>
          <td>
            <span class="badge badge-color">{{ repositoryInfo.vcs_instance_name }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'RepositoryInfoPanel',
  props: {
    repositoryInfo: {
      type: Object,
      required: true,
    },
  },
  components: {},
};
</script>
