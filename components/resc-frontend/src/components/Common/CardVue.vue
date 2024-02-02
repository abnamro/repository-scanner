<template>
  <div>
    <b-card class="card-box">
      <template #header>
        <div class="d-flex align-items-center justify-content-center fw-bold">
          <p class="mb-0 me-2">{{ title }}</p>
          <template v-if="titleIconDefinition">
            <FontAwesomeIcon
              :id="titleIconTooltipId"
              class="mb-0 me-2"
              :style="titleIconStyle"
              :icon="titleIconDefinition"
            />
            <b-tooltip :target="titleIconTooltipId" placement="right">
              {{ titleIconTooltip }}
            </b-tooltip>
          </template>
        </div>
      </template>

      <template #default>
        <div class="d-flex align-items-center justify-content-center fw-bold">
          <h5 class="mb-0 me-2 mt-2 justify-content-center text-center" :style="contentStyle">
            {{ formatCardBodyContent }}
          </h5>
          <FontAwesomeIcon
            v-if="contentIconDefinition"
            class="mb-0 me-2 mt-2 ml-1"
            :style="contentIconStyle"
            :icon="contentIconDefinition"
          />
        </div>
      </template>
    </b-card>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

export type CardIcon =
  | 'info-circle'
  | 'arrow-down'
  | 'arrow-up'
  | 'thumbs-down'
  | 'trophy'
  | 'medal'
  | 'award';

type Props = {
  cardTitle: string;
  cardBodyContent?: number | string;
  titleIcon?: CardIcon;
  titleIconColor?: string;
  titleIconTooltip?: string;
  contentColor?: string;
  contentIcon?: CardIcon;
  contentIconColor?: string;
};

const props = defineProps<Props>();

const title = ref(props.cardTitle);
const titleIconStyle = ref({
  color: props.titleIconColor,
  fontSize: '12px',
});
const contentIconStyle = ref({
  color: props.contentIconColor,
  fontSize: '20px',
});
const contentStyle = ref({
  color: props.contentIconColor,
  fontSize: '17px',
});

const titleIconDefinition = ref(props.titleIcon ? ['fas', props.titleIcon] : null);
const contentIconDefinition = ref(props.contentIcon ? ['fas', props.contentIcon] : null);
const formatCardBodyContent = ref(
  props.cardBodyContent ? props.cardBodyContent.toLocaleString() : '0'
);
const titleIconTooltip = ref(props.titleIconTooltip);
// This converts a tooltip in a HTML compliant ID
const titleIconTooltipId = ref(props.titleIconTooltip?.replace(/ /g, '') ?? 'no');
</script>
