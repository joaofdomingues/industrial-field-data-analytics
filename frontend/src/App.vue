<template>
  <main class="page">
    <header class="hero">
      <div class="hero-content">
        <p class="eyebrow">Field Data • Load Profiles • Reliability</p>
        <h1>Industrial Field Data Analytics</h1>
        <p class="subtitle">
          Engineering dashboard for monitoring industrial field telemetry, machine load profiles,
          anomaly indicators, energy consumption and reliability metrics.
        </p>

        <div class="hero-actions">
          <a :href="swaggerUrl" target="_blank" rel="noopener" class="link-button">
            API Docs
          </a>
          <a :href="backendUrl" target="_blank" rel="noopener" class="link-button secondary">
            Backend Health
          </a>
        </div>
      </div>

      <div class="hero-status">
        <div class="health" :class="apiOnline ? 'online' : 'offline'">
          <span class="pulse"></span>
          API {{ apiOnline ? 'Online' : 'Offline' }}
        </div>
        <p class="updated">Last sync: {{ lastUpdated || 'not loaded' }}</p>
      </div>
    </header>

    <section v-if="errorMessage" class="error-banner">
      {{ errorMessage }}
    </section>

    <section class="kpis">
      <div class="card">
        <span>Total Records</span>
        <strong>{{ kpis.total_records }}</strong>
        <small>Telemetry samples processed</small>
      </div>

      <div class="card">
        <span>Machines</span>
        <strong>{{ kpis.machines }}</strong>
        <small>Industrial assets monitored</small>
      </div>

      <div class="card">
        <span>Average Load</span>
        <strong>{{ kpis.average_load }}%</strong>
        <small>Mean operational load</small>
      </div>

      <div class="card">
        <span>Total Energy</span>
        <strong>{{ formatNumber(kpis.total_energy) }}</strong>
        <small>Aggregated consumption</small>
      </div>
    </section>

    <section class="status-grid">
      <div class="status-card critical">
        <span>Critical Issues</span>
        <strong>{{ kpis.critical_machines }}</strong>
        <small>Immediate engineering attention</small>
      </div>

      <div class="status-card warning">
        <span>Warning Issues</span>
        <strong>{{ kpis.warning_machines }}</strong>
        <small>Machines requiring monitoring</small>
      </div>

      <div class="status-card stable">
        <span>Health Score</span>
        <strong>{{ healthScore }}%</strong>
        <small>Estimated operational stability</small>
      </div>
    </section>

    <section class="filters">
      <div>
        <label>Machine Filter</label>
        <select v-model="selectedMachine" @change="loadDashboardData">
          <option value="All">All machines</option>
          <option
            v-for="machine in machines"
            :key="machine.machine_code"
            :value="machine.machine_code"
          >
            {{ machine.machine_code }} — {{ machine.machine_name }}
          </option>
        </select>
      </div>

      <div class="filter-info">
        <span>{{ selectedMachine === 'All' ? 'Global view' : `Focused on ${selectedMachine}` }}</span>
        <small>{{ loading ? 'Loading latest telemetry...' : 'Data loaded from production API' }}</small>
      </div>
    </section>

    <section class="grid-two">
      <div class="panel chart-panel">
        <div class="panel-header">
          <div>
            <h2>Load Profile</h2>
            <p>Average machine load over time</p>
          </div>
          <span class="chip">Time Series</span>
        </div>

        <div v-if="loading" class="skeleton chart-skeleton"></div>
        <Line v-else :data="loadChartData" :options="lineChartOptions" />
      </div>

      <div class="panel chart-panel">
        <div class="panel-header">
          <div>
            <h2>Energy by Machine</h2>
            <p>Aggregated energy consumption</p>
          </div>
          <span class="chip">Energy</span>
        </div>

        <div v-if="loading" class="skeleton chart-skeleton"></div>
        <Bar v-else :data="energyChartData" :options="barChartOptions" />
      </div>
    </section>

    <section class="grid-two">
      <div class="panel">
        <div class="panel-header">
          <div>
            <h2>Reliability Summary</h2>
            <p>Risk classification and estimated MTBF per machine</p>
          </div>
          <span class="chip">Reliability</span>
        </div>

        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Machine</th>
                <th>Zone</th>
                <th>Records</th>
                <th>Anomalies</th>
                <th>MTBF Hours</th>
                <th>Risk</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in reliability" :key="item.machine_code">
                <td>
                  <strong>{{ item.machine_name }}</strong>
                  <small>{{ item.machine_code }}</small>
                </td>
                <td>{{ item.factory_zone }}</td>
                <td>{{ item.records }}</td>
                <td>{{ item.anomaly_events }}</td>
                <td>{{ item.estimated_mtbf_hours || 'n/a' }}</td>
                <td>
                  <span class="badge" :class="riskClass(item.risk_level)">
                    {{ item.risk_level }}
                  </span>
                </td>
              </tr>
              <tr v-if="!reliability.length && !loading">
                <td colspan="6" class="empty">No reliability records available.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="panel">
        <div class="panel-header">
          <div>
            <h2>Active Alerts</h2>
            <p>Latest operational alerts generated from telemetry</p>
          </div>
          <span class="chip">Alerts</span>
        </div>

        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Machine</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="alert in alerts" :key="alert.machine_name + alert.alert_type + alert.message">
                <td>{{ alert.machine_name }}</td>
                <td>{{ alert.alert_type }}</td>
                <td>
                  <span class="badge" :class="riskClass(alert.severity)">
                    {{ alert.severity }}
                  </span>
                </td>
                <td>{{ alert.message }}</td>
              </tr>
              <tr v-if="!alerts.length && !loading">
                <td colspan="4" class="empty">No active alerts.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>Latest Field Data</h2>
          <p>Recent telemetry samples from deployed machines</p>
        </div>
        <span class="chip">Telemetry</span>
      </div>

      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Machine</th>
              <th>Zone</th>
              <th>Load %</th>
              <th>Temperature</th>
              <th>Vibration</th>
              <th>Energy</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in machineLoad.slice(0, 12)" :key="item.recorded_at + item.machine_code">
              <td>
                <strong>{{ item.machine_name }}</strong>
                <small>{{ item.machine_code }}</small>
              </td>
              <td>{{ item.factory_zone }}</td>
              <td>{{ item.load_percentage }}</td>
              <td>{{ item.temperature }}</td>
              <td>{{ item.vibration }}</td>
              <td>{{ item.energy_consumption }}</td>
              <td>{{ formatDate(item.recorded_at) }}</td>
            </tr>
            <tr v-if="!machineLoad.length && !loading">
              <td colspan="7" class="empty">No field data available.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>Data Quality Issues</h2>
          <p>Detected telemetry quality problems and threshold violations</p>
        </div>
        <span class="chip">Quality</span>
      </div>

      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Machine</th>
              <th>Issue</th>
              <th>Severity</th>
              <th>Value</th>
              <th>Threshold</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="issue in dataQuality" :key="issue.machine + issue.issue + issue.recorded_at">
              <td>{{ issue.machine }}</td>
              <td>{{ issue.issue }}</td>
              <td>
                <span class="badge" :class="riskClass(issue.severity)">
                  {{ issue.severity }}
                </span>
              </td>
              <td>{{ issue.value }}</td>
              <td>{{ issue.threshold }}</td>
            </tr>
            <tr v-if="!dataQuality.length && !loading">
              <td colspan="5" class="empty">No data quality issues detected.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script>
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Filler
} from 'chart.js'
import { Line, Bar } from 'vue-chartjs'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Filler
)

const API = import.meta.env.VITE_API_URL || 'https://industrial-field-data-analytics.onrender.com'

export default {
  components: { Line, Bar },

  data() {
    return {
      apiOnline: false,
      loading: false,
      errorMessage: '',
      selectedMachine: 'All',
      machines: [],
      machineLoad: [],
      loadProfiles: [],
      alerts: [],
      dataQuality: [],
      reliability: [],
      kpis: {
        total_records: 0,
        machines: 0,
        average_load: 0,
        total_energy: 0,
        critical_machines: 0,
        warning_machines: 0,
        stable_machines: 0
      },
      lastUpdated: null,
      backendUrl: `${API}/health/`,
      swaggerUrl: `${API}/api/docs/`
    }
  },

  computed: {
    healthScore() {
      const total = Number(this.kpis.machines || 0)
      const critical = Number(this.kpis.critical_machines || 0)
      const warning = Number(this.kpis.warning_machines || 0)

      if (!total) return 0

      const score = 100 - ((critical * 25 + warning * 10) / total)
      return Math.max(0, Math.round(score))
    },

    loadChartData() {
      return {
        labels: this.loadProfiles.map(item => this.formatHour(item.recorded_hour)),
        datasets: [
          {
            label: 'Load %',
            data: this.loadProfiles.map(item => Number(item.avg_load || 0)),
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.18)',
            pointBackgroundColor: '#e0f2fe',
            pointBorderColor: '#38bdf8',
            pointRadius: 4,
            pointHoverRadius: 6,
            borderWidth: 3,
            fill: true,
            tension: 0.35
          }
        ]
      }
    },

    energyChartData() {
      const grouped = {}

      this.machineLoad.forEach(item => {
        grouped[item.machine_name] =
          (grouped[item.machine_name] || 0) + Number(item.energy_consumption || 0)
      })

      return {
        labels: Object.keys(grouped),
        datasets: [
          {
            label: 'Energy Consumption',
            data: Object.values(grouped).map(v => Number(v.toFixed(2))),
            backgroundColor: 'rgba(34, 197, 94, 0.72)',
            borderColor: '#86efac',
            borderWidth: 1,
            borderRadius: 10
          }
        ]
      }
    },

    lineChartOptions() {
      return this.baseChartOptions('Load percentage')
    },

    barChartOptions() {
      return this.baseChartOptions('Energy consumption')
    }
  },

  mounted() {
    this.loadDashboardData()
  },

  methods: {
    baseChartOptions(label) {
      return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            labels: {
              color: '#cbd5e1',
              boxWidth: 14,
              usePointStyle: true
            }
          },
          tooltip: {
            backgroundColor: '#020617',
            titleColor: '#e5e7eb',
            bodyColor: '#cbd5e1',
            borderColor: 'rgba(148, 163, 184, 0.3)',
            borderWidth: 1
          },
          title: {
            display: false,
            text: label
          }
        },
        scales: {
          x: {
            ticks: {
              color: '#94a3b8',
              maxRotation: 0,
              autoSkip: true,
              maxTicksLimit: 8
            },
            grid: {
              color: 'rgba(148, 163, 184, 0.18)'
            }
          },
          y: {
            ticks: {
              color: '#94a3b8'
            },
            grid: {
              color: 'rgba(148, 163, 184, 0.24)'
            }
          }
        }
      }
    },

    async getJson(path) {
      const response = await fetch(`${API}${path}`)

      if (!response.ok) {
        throw new Error(`API error ${response.status} on ${path}`)
      }

      return response.json()
    },

    async loadDashboardData() {
      this.loading = true
      this.errorMessage = ''

      try {
        const suffix = this.selectedMachine !== 'All' ? `?machine=${this.selectedMachine}` : ''

        const dashboard = await this.getJson(`/engineering-summary/${suffix}`)

        this.apiOnline = dashboard.health?.status === 'ok'
        this.machines = dashboard.machines || []
        this.kpis = dashboard.kpis || this.kpis
        this.machineLoad = dashboard.latest_field_data || []
        this.loadProfiles = dashboard.load_profiles || []
        this.alerts = dashboard.alerts || []
        this.dataQuality = dashboard.data_quality || []
        this.reliability = dashboard.reliability || []
        this.lastUpdated = new Date().toLocaleTimeString()
      } catch (error) {
        this.apiOnline = false
        this.errorMessage = 'Unable to load production API data. Check backend availability or CORS configuration.'
        console.error(error)
      } finally {
        this.loading = false
      }
    },

    formatDate(value) {
      return value ? new Date(value).toLocaleString() : ''
    },

    formatHour(value) {
      return value
        ? new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        : ''
    },

    formatNumber(value) {
      const number = Number(value || 0)
      return number.toLocaleString(undefined, { maximumFractionDigits: 2 })
    },

    riskClass(value) {
      if (!value) return 'low'

      const normalized = String(value).toLowerCase()

      if (normalized.includes('critical') || normalized.includes('high')) return 'critical'
      if (normalized.includes('warning') || normalized.includes('medium')) return 'warning'
      return 'low'
    }
  }
}
</script>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: #0f172a;
}

.page {
  min-height: 100vh;
  padding: 32px;
  color: #f1f5f9;
  font-family: Inter, Arial, sans-serif;
  background:
    radial-gradient(circle at top left, rgba(14, 165, 233, 0.24), transparent 34%),
    radial-gradient(circle at top right, rgba(34, 197, 94, 0.16), transparent 34%),
    linear-gradient(180deg, #172033 0%, #0f172a 45%, #111827 100%);
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-start;
  margin-bottom: 28px;
}

.hero-content {
  max-width: 900px;
}

.eyebrow {
  color: #67e8f9;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 12px;
  font-weight: 800;
  margin: 0 0 12px;
}

h1 {
  margin: 0;
  font-size: clamp(32px, 5vw, 56px);
  letter-spacing: -0.04em;
  line-height: 1;
}

.subtitle {
  max-width: 850px;
  color: #cbd5e1;
  line-height: 1.7;
  font-size: 16px;
  margin-top: 18px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  margin-top: 22px;
  flex-wrap: wrap;
}

.link-button {
  text-decoration: none;
  color: #e0f2fe;
  background: rgba(14, 165, 233, 0.22);
  border: 1px solid rgba(56, 189, 248, 0.48);
  padding: 10px 14px;
  border-radius: 12px;
  font-weight: 700;
}

.link-button.secondary {
  color: #dcfce7;
  background: rgba(34, 197, 94, 0.18);
  border-color: rgba(34, 197, 94, 0.45);
}

.hero-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.health {
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 800;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pulse {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 18px currentColor;
}

.online {
  background: rgba(34, 197, 94, 0.2);
  color: #bbf7d0;
  border: 1px solid rgba(34, 197, 94, 0.5);
}

.offline {
  background: rgba(239, 68, 68, 0.2);
  color: #fecaca;
  border: 1px solid rgba(239, 68, 68, 0.5);
}

.updated,
.card small,
.status-card small,
.panel-header p,
.filter-info small,
td small {
  color: #cbd5e1;
}

.error-banner {
  border: 1px solid rgba(239, 68, 68, 0.45);
  background: rgba(239, 68, 68, 0.16);
  color: #fecaca;
  padding: 14px 16px;
  border-radius: 14px;
  margin-bottom: 20px;
}

.kpis,
.status-grid,
.grid-two {
  display: grid;
  gap: 18px;
  margin-bottom: 22px;
}

.kpis {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.status-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.grid-two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.card,
.panel,
.filters,
.status-card {
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid rgba(203, 213, 225, 0.22);
  border-radius: 22px;
  padding: 22px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.24);
  backdrop-filter: blur(14px);
}

.card {
  background: linear-gradient(180deg, rgba(51, 65, 85, 0.92), rgba(30, 41, 59, 0.9));
}

.panel {
  background: linear-gradient(180deg, rgba(30, 41, 59, 0.94), rgba(15, 23, 42, 0.92));
}

.card span,
.status-card span {
  color: #bfdbfe;
  font-size: 14px;
  font-weight: 700;
}

.card strong,
.status-card strong {
  display: block;
  margin-top: 8px;
  font-size: 34px;
  letter-spacing: -0.03em;
  color: #ffffff;
}

.card small,
.status-card small {
  display: block;
  margin-top: 8px;
  font-size: 13px;
}

.critical {
  border-color: rgba(248, 113, 113, 0.58);
}

.warning {
  border-color: rgba(251, 191, 36, 0.58);
}

.stable {
  border-color: rgba(74, 222, 128, 0.58);
}

.filters {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.filters label {
  display: block;
  font-size: 13px;
  color: #bfdbfe;
  font-weight: 700;
  margin-bottom: 8px;
}

select {
  min-width: 260px;
  background: #1e293b;
  color: #f8fafc;
  border: 1px solid #64748b;
  border-radius: 12px;
  padding: 11px 12px;
  outline: none;
}

.filter-info {
  text-align: right;
}

.filter-info span {
  display: block;
  font-weight: 800;
}

.panel {
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.panel-header h2 {
  margin: 0 0 6px;
  font-size: 19px;
  letter-spacing: -0.02em;
  color: #f8fafc;
}

.panel-header p {
  margin: 0;
  font-size: 14px;
}

.chip {
  border-radius: 999px;
  padding: 7px 10px;
  font-size: 12px;
  font-weight: 800;
  color: #e0f2fe;
  background: rgba(14, 165, 233, 0.22);
  border: 1px solid rgba(56, 189, 248, 0.38);
  white-space: nowrap;
}

.chart-panel {
  min-height: 420px;
}

.chart-panel canvas {
  min-height: 320px;
}

.skeleton {
  width: 100%;
  border-radius: 18px;
  background: linear-gradient(
    90deg,
    rgba(51, 65, 85, 0.75),
    rgba(71, 85, 105, 0.95),
    rgba(51, 65, 85, 0.75)
  );
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

.chart-skeleton {
  height: 320px;
}

@keyframes shimmer {
  to {
    background-position: -200% 0;
  }
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th,
td {
  padding: 13px 12px;
  border-bottom: 1px solid rgba(203, 213, 225, 0.18);
  text-align: left;
  vertical-align: top;
}

th {
  color: #bfdbfe;
  font-weight: 800;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

td {
  color: #e2e8f0;
}

td strong {
  display: block;
  color: #ffffff;
}

td small {
  display: block;
  margin-top: 3px;
  font-size: 12px;
}

tr:hover td {
  background: rgba(51, 65, 85, 0.45);
}

.badge {
  display: inline-block;
  border-radius: 999px;
  padding: 5px 10px;
  font-weight: 800;
  font-size: 12px;
  text-transform: uppercase;
}

.badge.critical {
  color: #fee2e2;
  background: rgba(239, 68, 68, 0.24);
  border: 1px solid rgba(248, 113, 113, 0.42);
}

.badge.warning {
  color: #fef3c7;
  background: rgba(245, 158, 11, 0.24);
  border: 1px solid rgba(251, 191, 36, 0.42);
}

.badge.low {
  color: #dcfce7;
  background: rgba(34, 197, 94, 0.22);
  border: 1px solid rgba(74, 222, 128, 0.36);
}

.empty {
  text-align: center;
  color: #cbd5e1;
  padding: 28px;
}

@media (max-width: 1100px) {
  .kpis {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .grid-two {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .page {
    padding: 20px;
  }

  .hero,
  .filters,
  .panel-header {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-status,
  .filter-info {
    align-items: flex-start;
    text-align: left;
  }

  .kpis,
  .status-grid {
    grid-template-columns: 1fr;
  }

  select {
    min-width: 100%;
  }
}
</style>