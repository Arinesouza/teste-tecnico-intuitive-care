<template>
  <div class="view-wrapper">
    <div class="container">
      <div class="nav-bar">
        <button class="btn-voltar" @click="$router.push('/operadoras')">← Voltar para Lista</button>
      </div>

      <div v-if="operadora" class="header-minimal">
        <h1 class="razao-social">{{ operadora.razao_social }}</h1>
        <div class="info-badges">
          <span><strong>CNPJ:</strong> {{ operadora.cnpj }}</span>
          <span class="separator">|</span>
          <span><strong>Registro ANS:</strong> {{ operadora.registro_ans }}</span>
          <span class="separator">|</span>
          <span><strong>Modalidade:</strong> {{ operadora.modalidade }}</span>
        </div>
      </div>

      <div class="card-financeiro">
        <div class="card-header">
          <h3>Histórico de Despesas Consolidadas</h3>
          <p>Valores apurados por período</p>
        </div>

        <div v-if="loading" class="loading">Buscando dados financeiros...</div>

        <div v-else-if="despesas.length > 0" class="table-container">
          <table class="tabela-destaque">
            <thead>
              <tr>
                <th>Ano</th>
                <th>Período (Trimestre)</th>
                <th class="text-right">Valor Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(d, i) in despesas" :key="i">
                <td class="col-ano">{{ d.ano }}</td>
                <td>{{ d.trimestre }}º Trimestre</td>
                <td class="col-valor text-right">{{ formatarMoeda(d.valor_despesa) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="sem-dados">
          <p>⚠️ Nenhuma despesa encontrada para esta operadora no banco de dados.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import api  from "../services/api";

const route = useRoute();
const operadora = ref(null);
const despesas = ref([]);
const loading = ref(true);

const formatarMoeda = (v) => {
  return Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

async function carregar() {
  loading.value = true;
  try {
    const cnpj = route.params.cnpj;
    const [resOp, resDesp] = await Promise.all([
      api.get(`/operadoras/${cnpj}`),
      api.get(`/operadoras/${cnpj}/despesas`)
    ]);
    operadora.value = resOp.data;
    despesas.value = resDesp.data;
  } catch (err) {
    console.error("Erro ao carregar:", err);
  } finally {
    loading.value = false;
  }
}

onMounted(carregar);
</script>

<style scoped>
.view-wrapper { background-color: #f8fafc; min-height: 100vh; padding: 40px 0; }
.container { max-width: 1000px; margin: 0 auto; padding: 0 20px; text-align: center; }

.nav-bar { text-align: left; margin-bottom: 30px; }
.btn-voltar { 
  background: white; border: 1px solid #e2e8f0; padding: 10px 20px; 
  border-radius: 8px; cursor: pointer; font-weight: 600; color: #64748b;
  transition: all 0.2s;
}
.btn-voltar:hover { background: #f1f5f9; color: #1e293b; }

.header-minimal { margin-bottom: 40px; }
.razao-social { font-size: 32px; color: #0f172a; font-weight: 800; margin-bottom: 15px; }
.info-badges { font-size: 16px; color: #64748b; margin-bottom: 10px; }
.separator { margin: 0 15px; color: #cbd5e1; }
.localizacao { font-size: 18px; color: #334155; font-weight: 500; }

.card-financeiro { 
  background: white; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0; overflow: hidden;
}
.card-header { padding: 30px; border-bottom: 1px solid #f1f5f9; background: #fff; text-align: left; }
.card-header h3 { font-size: 20px; color: #1e293b; margin-bottom: 5px; }
.card-header p { color: #94a3b8; font-size: 14px; }

.table-container { padding: 20px; }
.tabela-destaque { width: 100%; border-collapse: collapse; }
.tabela-destaque th { 
  text-align: left; padding: 15px; background: #f8fafc; 
  color: #64748b; font-weight: 700; text-transform: uppercase; font-size: 12px;
}
.tabela-destaque td { padding: 20px 15px; border-bottom: 1px solid #f1f5f9; text-align: left; font-size: 16px; }

.col-ano { font-weight: 700; color: #1e293b; }
.col-valor { color: #dc2626; font-weight: 800; font-size: 18px; }
.text-right { text-align: right !important; }

.loading, .sem-dados { padding: 60px; color: #94a3b8; font-weight: 600; }
</style>