<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { api } from "../services/api";

const router = useRouter();
const operadoras = ref([]);
const loading = ref(false);
const page = ref(1);
const limit = ref(12);
const total = ref(0);
const search = ref("");

async function carregar() {
  loading.value = true;
  try {
    const response = await api.get("/operadoras", {
      params: { 
        page: page.value, 
        limit: limit.value, 
        ...(search.value ? { search: search.value } : {}) 
      },
    });
    operadoras.value = response.data.data ?? [];
    total.value = response.data.total ?? 0;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {
    console.error("Erro ao carregar operadoras:", err);
  } finally {
    loading.value = false;
  }
}

function irParaDetalhe(cnpj) {
  router.push(`/operadoras/${cnpj}`);
}

watch(page, () => {
  carregar();
});

watch(search, () => {
  page.value = 1;
  carregar();
});

onMounted(carregar);
</script>

<template>
  <div class="view-wrapper">
    <div class="container">
      <div style="text-align: left; margin-bottom: 10px;">
        <button class="btn-dash" @click="router.push('/')">← Dashboard</button>
      </div>

      <div class="header">
        <h1>Operadoras de Saúde</h1>
        <p class="subtitle">Base de dados ANS - Consulta Consolidada</p>
        <input 
          v-model="search" 
          placeholder="Busque por Nome ou CNPJ..." 
          class="search-input" 
        />
      </div>

      <div v-if="loading" class="loading-state">⏳ Sincronizando com o banco...</div>

      <div v-else class="grid">
        <div 
          v-for="op in operadoras" 
          :key="op.cnpj" 
          class="card" 
          @click="irParaDetalhe(op.cnpj)"
        >
          <div class="card-content">
            <h3 class="clamp-text">{{ op.razao_social }}</h3>
            <p class="cnpj-label"><strong>CNPJ:</strong> {{ op.cnpj }}</p>
            <div class="footer-card">
              <span class="tag">{{ op.modalidade }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="pagination" v-if="total > limit">
        <button @click="page--" :disabled="page === 1">Anterior</button>
        <span class="page-info">Página {{ page }} de {{ Math.ceil(total / limit) }}</span>
        <button @click="page++" :disabled="page * limit >= total">Próxima</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.btn-dash { padding: 8px 15px; font-size: 13px; border: 1px solid #ddd; background: #fff; color: #666; }
.view-wrapper { width: 100%; min-height: 100vh; background-color: #f4f7f6; color: #2c3e50; display: block; text-align: left; }
.container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
.header { margin-bottom: 40px; text-align: center; }
.header h1 { font-size: 2.5rem; margin-bottom: 5px; color: #1a2a3a; }
.subtitle { color: #7f8c8d; margin-bottom: 25px; }
.search-input { width: 100%; max-width: 600px; padding: 15px; border: 1px solid #dcdde1; border-radius: 10px; font-size: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); outline: none; }
.search-input:focus { border-color: #3498db; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 25px; }
.card { border: 1px solid #e1e1e1; border-radius: 15px; background: #ffffff; cursor: pointer; transition: all 0.3s ease; overflow: hidden; }
.card:hover { transform: translateY(-5px); box-shadow: 0 12px 24px rgba(0,0,0,0.1); border-color: #3498db; }
.card-content { padding: 25px; }
.clamp-text { display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 2.8em; font-size: 17px; color: #2c3e50; margin-bottom: 12px; line-height: 1.4; }
.cnpj-label { font-size: 14px; color: #95a5a6; }
.tag { display: inline-block; background: #ebf5fb; color: #3498db; padding: 5px 12px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.footer-card { margin-top: 15px; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 30px; margin-top: 50px; }
.page-info { font-weight: 600; color: #7f8c8d; }
button { padding: 12px 24px; border-radius: 8px; border: 1px solid #3498db; background: #fff; color: #3498db; cursor: pointer; font-weight: bold; transition: 0.2s; }
button:hover:not(:disabled) { background: #3498db; color: #fff; }
button:disabled { opacity: 0.3; cursor: not-allowed; }
.loading-state { text-align: center; padding: 80px; font-size: 1.2rem; color: #34495e; }
</style>