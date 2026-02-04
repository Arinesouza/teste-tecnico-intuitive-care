import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import Operadoras from "../views/Operadoras.vue";
import OperadoraDetalhe from "../views/OperadoraDetalhe.vue";

const routes = [
  {
    path: "/",
    name: "Dashboard",
    component: Dashboard,
  },
  {
    path: "/operadoras",
    name: "Operadoras",
    component: Operadoras,
  },
  {
    path: "/operadoras/:cnpj",
    name: "OperadoraDetalhe",
    component: OperadoraDetalhe,
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;