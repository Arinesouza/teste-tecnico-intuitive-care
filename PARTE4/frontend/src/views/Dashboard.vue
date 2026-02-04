<template>
  <div class="view-wrapper">
    <div class="container">
      <div class="header">
        <h1>Dashboard Analítico</h1>
        <p class="subtitle">Visão Geral de Despesas por Estado (UF)</p>
      </div>

      <div class="chart-box">
        <DespesasPorUFChart />
      </div>

      <div class="actions">
        <router-link to="/operadoras" class="btn-main">
          Acessar Lista Completa de Operadoras →
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import DespesasPorUFChart from "../components/DespesasPorUFChart.vue";
</script>

<style scoped>
.view-wrapper { min-height: 100vh; background-color: #f8fafc; padding: 40px 20px; }
.container { max-width: 1000px; margin: 0 auto; }
.header { text-align: center; margin-bottom: 40px; }
.header h1 { font-size: 2.5rem; color: #0f172a; }
.subtitle { color: #64748b; font-size: 1.1rem; }
.chart-box { background: white; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); }
.actions { margin-top: 50px; text-align: center; }
.btn-main { 
  background: #3b82f6; color: white; padding: 18px 36px; 
  border-radius: 12px; text-decoration: none; font-weight: 700;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4); transition: all 0.2s;
}
.btn-main:hover { background: #2563eb; transform: translateY(-2px); }
</style>