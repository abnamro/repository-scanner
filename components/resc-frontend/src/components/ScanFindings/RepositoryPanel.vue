<template>
  <div class="row">
    <table class="table table-sm table-borderless" aria-hidden="true">
      <tbody>
        <tr>
          <th>VCS Instance</th>
          <td>
            <span class="badge bg-secondary">{{ props.vcs_instance.name }}</span>
          </td>
        </tr>
        <tr>
          <th>Project</th>
          <td>
            <span class="badge bg-secondary">{{ props.repository.project_key }}</span>
          </td>
        </tr>
        <tr>
          <th>Repository</th>
          <td>
            <span class="badge bg-secondary">{{ props.repository.repository_name }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type { RepositoryRead, VCSInstanceRead } from '@/services/shema-to-types';

type Props = {
  repository: RepositoryRead;
  vcs_instance: VCSInstanceRead;
};

const props = defineProps<Props>();
</script>
