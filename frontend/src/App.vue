<template>
  <main class="page">
    <header class="hero">
      <div>
        <p class="eyebrow">Field Data • Load Profiles • Reliability</p>
        <h1>Industrial Field Data Analytics</h1>
        <p class="subtitle">
          Vue + Django dashboard for engineering teams that need fast access to machine load profiles,
          anomaly indicators and reliability metrics from field telemetry.
        </p>
      </div>
      <div class="health" :class="apiOnline ? 'online' : 'offline'">
        API {{ apiOnline ? 'Online' : 'Offline' }}
      </div>
    </header>

    <section class="kpis">
      <div class="card"><span>Total Records</span><strong>{{ kpis.total_records }}</strong></div>
      <div class="card"><span>Machines</span><strong>{{ kpis.machines }}</strong></div>
      <div class="card"><span>Average Load</span><strong>{{ kpis.average_load }}%</strong></div>
      <div class="card"><span>Total Energy</span><strong>{{ kpis.total_energy }}</strong></div>
    </section>

    <section class="status-grid">
      <div class="status-card critical"><span>Critical Issues</span><strong>{{ kpis.critical_machines }}</strong></div>
      <div class="status-card warning"><span>Warning Issues</span><strong>{{ kpis.warning_machines }}</strong></div>
      <div class="status-card stable"><span>Stable Records</span><strong>{{ kpis.stable_machines }}</strong></div>
    </section>

    <section class="filters">
      <label>Machine</label>
      <select v-model="selectedMachine" @change="loadDashboardData">
        <option value="All">All machines</option>
        <option v-for="machine in machines" :key="machine.machine_code" :value="machine.machine_code">
          {{ machine.machine_code }} — {{ machine.machine_name }}
        </option>
      </select>
      <span class="updated">Last updated: {{ lastUpdated || 'not loaded' }}</span>
    </section>

    <section class="grid-two">
      <div class="panel">
        <h2>Load Profile</h2>
        <Line :data="loadChartData" :options="chartOptions" />
      </div>
      <div class="panel">
        <h2>Energy by Machine</h2>
        <Bar :data="energyChartData" :options="chartOptions" />
      </div>
    </section>

    <section class="panel">
      <h2>Reliability Summary</h2>
      <table>
        <thead>
          <tr><th>Machine</th><th>Zone</th><th>Records</th><th>Anomalies</th><th>MTBF Hours</th><th>Risk</th></tr>
        </thead>
        <tbody>
          <tr v-for="item in reliability" :key="item.machine_code">
            <td>{{ item.machine_name }}</td>
            <td>{{ item.factory_zone }}</td>
            <td>{{ item.records }}</td>
            <td>{{ item.anomaly_events }}</td>
            <td>{{ item.estimated_mtbf_hours || 'n/a' }}</td>
            <td><span class="badge" :class="item.risk_level.toLowerCase()">{{ item.risk_level }}</span></td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="panel">
      <h2>Latest Field Data</h2>
      <table>
        <thead>
          <tr><th>Machine</th><th>Zone</th><th>Load %</th><th>Temp</th><th>Vibration</th><th>Energy</th><th>Timestamp</th></tr>
        </thead>
        <tbody>
          <tr v-for="item in machineLoad" :key="item.recorded_at + item.machine_code">
            <td>{{ item.machine_name }}</td>
            <td>{{ item.factory_zone }}</td>
            <td>{{ item.load_percentage }}</td>
            <td>{{ item.temperature }}</td>
            <td>{{ item.vibration }}</td>
            <td>{{ item.energy_consumption }}</td>
            <td>{{ formatDate(item.recorded_at) }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="grid-two">
      <div class="panel">
        <h2>Data Quality Issues</h2>
        <table>
          <thead><tr><th>Machine</th><th>Issue</th><th>Severity</th><th>Value</th><th>Threshold</th></tr></thead>
          <tbody>
            <tr v-for="issue in dataQuality" :key="issue.machine + issue.issue + issue.recorded_at">
              <td>{{ issue.machine }}</td><td>{{ issue.issue }}</td>
              <td><span class="badge" :class="issue.severity.toLowerCase()">{{ issue.severity }}</span></td>
              <td>{{ issue.value }}</td><td>{{ issue.threshold }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="panel">
        <h2>Active Alerts</h2>
        <table>
          <thead><tr><th>Machine</th><th>Type</th><th>Severity</th><th>Message</th></tr></thead>
          <tbody>
            <tr v-for="alert in alerts" :key="alert.machine__machine_name + alert.alert_type">
              <td>{{ alert.machine_name }}</td><td>{{ alert.alert_type }}</td>
              <td><span class="badge" :class="alert.severity.toLowerCase()">{{ alert.severity }}</span></td>
              <td>{{ alert.message }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script>
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, BarElement, CategoryScale, LinearScale, PointElement } from 'chart.js'
import { Line, Bar } from 'vue-chartjs'

ChartJS.register(Title, Tooltip, Legend, LineElement, BarElement, CategoryScale, LinearScale, PointElement)

const API = import.meta.env.VITE_API_URL || 'https://industrial-field-data-analytics.onrender.com'

export default {
  components: { Line, Bar },
  data() {
    return {
      apiOnline: false,
      selectedMachine: 'All',
      machines: [],
      machineLoad: [],
      loadProfiles: [],
      alerts: [],
      dataQuality: [],
      reliability: [],
      kpis: { total_records: 0, machines: 0, average_load: 0, total_energy: 0, critical_machines: 0, warning_machines: 0, stable_machines: 0 },
      lastUpdated: null,
      chartOptions: { responsive: true, maintainAspectRatio: false }
    }
  },
  computed: {
    loadChartData() {
      return {
        labels: this.loadProfiles.map(item => this.formatHour(item.recorded_hour)),
        datasets: [{ label: 'Load %', data: this.loadProfiles.map(item => item.avg_load) }]
      }
    },
    energyChartData() {
      const grouped = {}
      this.machineLoad.forEach(item => {
        grouped[item.machine_name] = (grouped[item.machine_name] || 0) + Number(item.energy_consumption || 0)
      })
      return { labels: Object.keys(grouped), datasets: [{ label: 'Energy Consumption', data: Object.values(grouped).map(v => v.toFixed(2)) }] }
    }
  },
  mounted() { this.loadDashboardData() },
  methods: {
    async getJson(path) {
      const response = await fetch(`${API}${path}`)
      if (!response.ok) throw new Error(`API error ${response.status}`)
      return response.json()
    },
    async loadDashboardData() {
      try {
        const suffix = this.selectedMachine !== 'All' ? `?machine=${this.selectedMachine}` : ''
        const [health, machines, kpis, load, profiles, alerts, quality, reliability] = await Promise.all([
          this.getJson('/health/'), this.getJson('/machines/'), this.getJson('/kpis/'),
          this.getJson(`/machine-load/${suffix}`), this.getJson(`/load-profiles/${suffix}`),
          this.getJson('/alerts/'), this.getJson('/data-quality/'), this.getJson('/reliability/summary/')
        ])
        this.apiOnline = health.status === 'ok'
        this.machines = machines
        this.kpis = kpis
        this.machineLoad = load
        this.loadProfiles = profiles
        this.alerts = alerts
        this.dataQuality = quality
        this.reliability = reliability
        this.lastUpdated = new Date().toLocaleTimeString()
      } catch (error) {
        this.apiOnline = false
        console.error(error)
      }
    },
    formatDate(value) { return value ? new Date(value).toLocaleString() : '' },
    formatHour(value) { return value ? new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '' }
  }
}
</script>

<style>
* { box-sizing: border-box; }
body { margin: 0; background: #0f172a; }
.page { min-height: 100vh; padding: 32px; color: #e5e7eb; font-family: Inter, Arial, sans-serif; background: radial-gradient(circle at top, #1e293b, #020617); }
.hero { display: flex; justify-content: space-between; gap: 24px; align-items: start; margin-bottom: 24px; }
.eyebrow { color: #38bdf8; text-transform: uppercase; letter-spacing: 0.12em; font-size: 12px; font-weight: 700; }
h1 { margin: 0; font-size: 38px; }
.subtitle { max-width: 820px; color: #94a3b8; line-height: 1.6; }
.health { border-radius: 999px; padding: 10px 16px; font-weight: 700; white-space: nowrap; }
.online { background: rgba(34,197,94,.15); color: #86efac; border: 1px solid rgba(34,197,94,.4); }
.offline { background: rgba(239,68,68,.15); color: #fca5a5; border: 1px solid rgba(239,68,68,.4); }
.kpis, .status-grid, .grid-two { display: grid; gap: 16px; margin-bottom: 20px; }
.kpis { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.status-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid-two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.card, .panel, .filters, .status-card { background: rgba(15, 23, 42, .84); border: 1px solid rgba(148, 163, 184, .18); border-radius: 18px; padding: 20px; box-shadow: 0 20px 60px rgba(0, 0, 0, .26); }
.card span, .status-card span, .updated { color: #94a3b8; font-size: 14px; }
.card strong, .status-card strong { display: block; margin-top: 8px; font-size: 30px; }
.critical { border-color: rgba(239,68,68,.45); }
.warning { border-color: rgba(245,158,11,.45); }
.stable { border-color: rgba(34,197,94,.45); }
.filters { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
select { background: #020617; color: #e5e7eb; border: 1px solid #334155; border-radius: 10px; padding: 10px 12px; }
.panel { overflow: auto; }
.panel canvas { min-height: 300px; }
h2 { margin-top: 0; font-size: 18px; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { padding: 12px; border-bottom: 1px solid rgba(148, 163, 184, .16); text-align: left; }
th { color: #93c5fd; font-weight: 700; }
.badge { display: inline-block; border-radius: 999px; padding: 4px 9px; font-weight: 700; font-size: 12px; }
.badge.critical, .badge.high { color: #fecaca; background: rgba(239,68,68,.18); }
.badge.warning, .badge.medium { color: #fde68a; background: rgba(245,158,11,.18); }
.badge.low { color: #bbf7d0; background: rgba(34,197,94,.18); }
@media (max-width: 900px) { .kpis, .status-grid, .grid-two { grid-template-columns: 1fr; } .hero, .filters { flex-direction: column; align-items: stretch; } }
</style>
