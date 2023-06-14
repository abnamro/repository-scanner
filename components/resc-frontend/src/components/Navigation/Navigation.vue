<script>
export default {
  name: 'Navigation',
  sidebarMenu: [
    {
      header: true,
      title: 'RESC',
    },
    {
      href: '/',
      title: 'ANALYTICS',
      icon: {
        element: 'font-awesome-icon',
        attributes: {
          icon: 'chart-line',
        },
      },
      child: [
        {
          href: '/metrics/audit-metrics',
          title: 'Audit Metrics',
          icon: {
            element: 'font-awesome-icon',
            attributes: {
              icon: 'chart-bar',
            },
          },
        },
        {
          href: '/metrics/finding-metrics',
          title: 'Finding Metrics',
          icon: {
            element: 'font-awesome-icon',
            attributes: {
              icon: 'chart-bar',
            },
          },
        },
        {
          href: '/metrics/rule-metrics',
          title: 'Rule Metrics',
          icon: {
            element: 'font-awesome-icon',
            attributes: {
              icon: 'chart-bar',
            },
          },
        },
      ],
    },
    {
      href: '/repositories',
      title: 'REPOSITORIES',
      icon: {
        element: 'font-awesome-icon',
        attributes: {
          icon: 'code-branch',
        },
      },
    },
    {
      href: '/rule-analysis',
      title: 'RULE ANALYSIS',
      icon: {
        element: 'font-awesome-icon',
        attributes: {
          icon: 'hammer',
        },
      },
    },
    {
      href: '/rulepacks',
      title: 'RULEPACKS',
      icon: {
        element: 'font-awesome-icon',
        attributes: {
          icon: 'shield-alt',
        },
      },
    },
  ],
};
</script>
