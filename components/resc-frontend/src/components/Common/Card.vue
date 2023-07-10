<template>
  <div>
    <b-card class="card-box">
      <template #header>
        <div class="d-flex align-items-center justify-content-center font-weight-bold">
          <p class="mb-0 mr-2">{{ title }}</p>
          <font-awesome-icon
            v-if="titleIconDefinition"
            :id="titleIconTooltip"
            class="mb-0 mr-2"
            :style="titleIconStyle"
            :icon="titleIconDefinition"
          />
          <b-tooltip v-if="titleIconDefinition" :target="titleIconTooltip" placement="right">{{
            titleIconTooltip
          }}</b-tooltip>
        </div>
      </template>

      <template #default>
        <div class="d-flex align-items-center justify-content-center font-weight-bold">
          <h5 class="mb-0 mr-2 mt-2 justify-content-center text-center" :style="contentStyle">
            {{ formatCardBodyContent }}
          </h5>
          <font-awesome-icon
            v-if="contentIconDefinition"
            class="mb-0 mr-2 mt-2 ml-1"
            :style="contentIconStyle"
            :icon="contentIconDefinition"
          />
        </div>
      </template>
    </b-card>
  </div>
</template>
<script>
export default {
  name: 'Card',
  props: {
    cardTitle: {
      type: String,
      required: true,
    },
    cardBodyContent: {
      required: true,
    },
    titleIcon: {
      type: String,
      required: false,
    },
    titleIconColor: {
      type: String,
      required: false,
    },
    titleIconTooltip: {
      type: String,
      required: false,
    },
    contentColor: {
      type: String,
      required: false,
    },
    contentIcon: {
      type: String,
      required: false,
    },
    contentIconColor: {
      type: String,
      required: false,
    },
    contentIconTooltip: {
      type: String,
      required: false,
    },
  },
  data() {
    return {
      title: this.cardTitle,
      content: this.cardBodyContent,
      titleIconStyle: {
        color: this.titleIconColor,
        fontSize: '12px',
      },
      contentIconStyle: {
        color: this.contentIconColor,
        fontSize: '20px',
      },
      contentStyle: {
        color: this.contentIconColor,
        fontSize: '17px',
      },
    };
  },
  methods: {},
  computed: {
    titleIconDefinition() {
      return this.titleIcon ? ['fas', this.titleIcon] : null;
    },
    contentIconDefinition() {
      return this.contentIcon ? ['fas', this.contentIcon] : null;
    },
    formatCardBodyContent() {
      return this.cardBodyContent ? this.cardBodyContent.toLocaleString() : 0;
    },
  },
  watch: {
    contentColor(newValue) {
      this.contentStyle.color = newValue;
    },
    contentIconColor(newValue) {
      this.contentIconStyle.color = newValue;
    },
  },
};
</script>
