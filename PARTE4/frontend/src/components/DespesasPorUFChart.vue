<template>
  <div class="chart-container">
    <h3>Distribuição de Despesas por UF (Top 10)</h3>
    <div v-if="loading" class="chart-loading">
      <div class="spinner"></div>
      <p>Calculando estatísticas por estado...</p>
    </div>
    <div v-else-if="error" class="chart-error">Erro ao carregar o gráfico de UFs.</div>
    <div v-else>
      <apexchart type="bar" height="380" :options="chartOptions" :series="series"></apexchart>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { api } from '../services/api';

const loading = ref(true);
const error = ref(false);
const chartData = ref([]);


const formatarMoedaAbreviada = (val) => {
  if (val >= 1e9) return 'R$ ' + (val / 1e9).toFixed(1) + 'B';
  if (val >= 1e6) return 'R$ ' + (val / 1e6).toFixed(1) + 'M';
  return val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const chartOptions = ref({
  chart: { type: 'bar', toolbar: { show: false } },
  plotOptions: {
    bar: { horizontal: true, barHeight: '60%', dataLabels: { position: 'top' } }
  },
  xaxis: {
    categories: [], 
    labels: {
      formatter: (val) => {
        if (val >= 1e12) return (val / 1e12).toFixed(1) + 'T';
        if (val >= 1e9) return (val / 1e9).toFixed(1) + 'B';
        return (val / 1e6).toFixed(0) + 'M';
      }
    }
  },
  dataLabels: {
    enabled: true,
    offsetX: 35,
    style: { fontSize: '12px', colors: ['#475569'] },
    formatter: (val) => {
       if (val >= 1e9) return 'R$ ' + (val / 1e9).toFixed(1) + 'B';
       return 'R$ ' + (val / 1e6).toFixed(0) + 'M';
    }
  }
});

const series = ref([{
  name: 'Total em Despesas',
  data: []
}]);

async function fetchChartData() {
  try {
    const response = await api.get('/estatisticas/despesas_por_uf');
    chartData.value = response.data;

    chartOptions.value.xaxis.categories = chartData.value.map(item => item.label);
    series.value[0].data = chartData.value.map(item => item.valor);
  } catch (err) {
    console.error('Erro ao buscar estatísticas:', err);
    error.value = true;
  } finally {
    loading.value = false;
  }
}

onMounted(fetchChartData);
</script>

<style scoped>
.chart-container {
  background: #ffffff;
  padding: 30px;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  margin: 30px 0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

h3 {
  text-align: left;
  margin-bottom: 25px;
  color: #0f172a;
  font-size: 1.25rem;
  font-weight: 700;
}

.chart-loading, .chart-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #64748b;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>